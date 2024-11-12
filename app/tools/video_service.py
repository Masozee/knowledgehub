import os
import json
import tempfile
import subprocess
import logging
from datetime import datetime
import re
from openai import OpenAI
import whisper
import yt_dlp
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from .models import *

logger = logging.getLogger(__name__)


class CleanupMixin:
    """Mixin for safe file and model cleanup operations"""

    def safe_delete_file(self, file_path):
        """Safely delete a file if it exists"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")

    def safe_delete_dir(self, dir_path):
        """Safely delete a directory and its contents"""
        try:
            if dir_path and os.path.exists(dir_path):
                import shutil
                shutil.rmtree(dir_path)
                logger.info(f"Deleted directory: {dir_path}")
        except Exception as e:
            logger.error(f"Error deleting directory {dir_path}: {str(e)}")

    def cleanup_model_instance(self, instance):
        """Clean up model instance and related files"""
        try:
            # Skip if instance doesn't exist or hasn't been saved
            if not instance or not instance.id:
                return

            if hasattr(instance, 'video_file') and instance.video_file:
                instance.video_file.delete(save=False)

            if isinstance(instance, VideoContent):
                # Clean up transcript files
                for field in ['transcript_txt_path', 'transcript_json_path',
                              'transcript_srt_path', 'transcript_vtt_path']:
                    if hasattr(instance, field) and getattr(instance, field):
                        self.safe_delete_file(getattr(instance, field))

                # Clean up related VideoNote if exists
                if hasattr(instance, 'video_note'):
                    video_note = instance.video_note
                    if video_note and video_note.id:
                        self.cleanup_model_instance(video_note)

            elif isinstance(instance, VideoNote):
                # Clean up related conversation and messages
                if instance.conversation and instance.conversation.id:
                    Message.objects.filter(conversation=instance.conversation).delete()
                    instance.conversation.delete()

            # Delete the instance itself if it exists in the database
            if instance.id:
                instance.delete()
                logger.info(f"Cleaned up {instance.__class__.__name__} instance and related files")

        except Exception as e:
            logger.error(f"Error cleaning up instance: {str(e)}")
            # Don't raise the exception to allow the cleanup process to continue
            pass

    def safe_cleanup(self, instance, related_instances=None):
        """Safely clean up instance and related instances"""
        try:
            # Clean up related instances first
            if related_instances:
                for related in related_instances:
                    if related:
                        self.cleanup_model_instance(related)

            # Clean up main instance
            if instance:
                self.cleanup_model_instance(instance)

        except Exception as e:
            logger.error(f"Error in safe cleanup: {str(e)}")


class VideoChunker:
    """Handles video chunking for processing"""

    def create_chunks(self, video_path, output_dir, chunk_duration=300):
        """Split video into chunks of specified duration"""
        try:
            # Get video duration
            duration_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            duration = float(subprocess.check_output(duration_cmd).decode().strip())

            chunk_paths = []
            for start_time in range(0, int(duration), chunk_duration):
                output_path = os.path.join(output_dir, f'chunk_{start_time}.mp4')

                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', video_path,
                    '-ss', str(start_time),
                    '-t', str(chunk_duration),
                    '-c', 'copy',
                    '-y',
                    output_path
                ]

                subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                chunk_paths.append(output_path)

            return chunk_paths

        except Exception as e:
            logger.error(f"Error creating video chunks: {str(e)}")
            raise


class VideoProcessor(CleanupMixin):
    def __init__(self, user, output_dir=None):
        self.user = user
        self.model = whisper.load_model("base")
        self.chunker = VideoChunker()
        self.output_dir = output_dir or os.path.join(settings.MEDIA_ROOT, 'transcripts')
        self.transcript_downloader = TranscriptDownloader(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Initialized VideoProcessor for user: {user.id}")

    def cleanup_model_instance(self, instance):
        """Clean up model instance and related files"""
        try:
            if hasattr(instance, 'video_file') and instance.video_file:
                instance.video_file.delete(save=False)

            if isinstance(instance, VideoContent):
                # Clean up transcript files
                for field in ['transcript_txt_path', 'transcript_json_path',
                              'transcript_srt_path', 'transcript_vtt_path']:
                    if hasattr(instance, field) and getattr(instance, field):
                        self.safe_delete_file(getattr(instance, field))

                # Clean up related VideoNote if exists
                if hasattr(instance, 'video_note'):
                    self.cleanup_model_instance(instance.video_note)

            elif isinstance(instance, VideoNote):
                # Clean up related conversation and messages
                if instance.conversation:
                    Message.objects.filter(conversation=instance.conversation).delete()
                    instance.conversation.delete()

            # Delete the instance itself
            instance.delete()
            logger.info(f"Cleaned up {instance.__class__.__name__} instance and related files")

        except Exception as e:
            logger.error(f"Error cleaning up instance: {str(e)}")
            raise

    def process_youtube_url(self, url, save_txt=False):
        """Process a YouTube video URL"""
        video_content = None
        temp_dir = None
        downloaded_file = None
        related_instances = []

        try:
            logger.info(f"Processing YouTube URL: {url}")
            temp_dir = tempfile.mkdtemp()

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'quiet': True,
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(temp_dir, 'original.mp4'),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = os.path.join(temp_dir, 'original.mp4')

                if not os.path.exists(downloaded_file):
                    raise FileNotFoundError("Downloaded video file not found")

                video_content = VideoContent.objects.create(
                    title=info.get('title', 'Untitled Video'),
                    source_url=url,
                    duration=info.get('duration', 0)
                )
                logger.info(f"Created VideoContent: {video_content.id}")

                result = self._process_video_in_chunks(video_content, downloaded_file, save_txt)
                related_instances.append(result)

                with open(downloaded_file, 'rb') as f:
                    video_content.video_file.save(f'{video_content.id}.mp4', ContentFile(f.read()))

                return result

        except Exception as e:
            logger.error(f"Error processing YouTube video: {str(e)}")
            self.safe_cleanup(video_content, related_instances)
            raise

        finally:
            self.safe_delete_file(downloaded_file)
            self.safe_delete_dir(temp_dir)

    def process_local_video(self, video_file, save_txt=False):
        """Process a locally uploaded video file"""
        video_content = None
        temp_dir = None
        related_instances = []

        try:
            logger.info(f"Processing local video: {video_file.name}")
            temp_dir = tempfile.mkdtemp()

            video_path = os.path.join(temp_dir, 'original.mp4')
            with open(video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)

            video_content = VideoContent.objects.create(
                title=os.path.splitext(video_file.name)[0]
            )
            logger.info(f"Created VideoContent: {video_content.id}")

            result = self._process_video_in_chunks(video_content, video_path, save_txt)
            related_instances.append(result)

            video_content.video_file.save(f'{video_content.id}.mp4', video_file)

            return result

        except Exception as e:
            logger.error(f"Error processing local video: {str(e)}")
            self.safe_cleanup(video_content, related_instances)
            raise

        finally:
            self.safe_delete_dir(temp_dir)

    def process_local_video(self, video_file, save_txt=False):
        """Process a locally uploaded video file"""
        video_content = None
        temp_dir = None

        try:
            logger.info(f"Processing local video: {video_file.name}")
            temp_dir = tempfile.mkdtemp()

            video_path = os.path.join(temp_dir, 'original.mp4')
            with open(video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)

            video_content = VideoContent.objects.create(
                title=os.path.splitext(video_file.name)[0]
            )
            logger.info(f"Created VideoContent: {video_content.id}")

            result = self._process_video_in_chunks(video_content, video_path, save_txt)
            video_content.video_file.save(f'{video_content.id}.mp4', video_file)

            return result

        except Exception as e:
            logger.error(f"Error processing local video: {str(e)}")
            if video_content:
                self.cleanup_model_instance(video_content)
            raise

        finally:
            self.safe_delete_dir(temp_dir)

    def process_video_with_subtitles(self, video_file_or_url, is_url=False, save_formats=True):
        """Process video with automatic subtitle generation and analysis"""
        video_content = None
        try:
            if is_url:
                result = self.process_youtube_url(video_file_or_url, save_txt=save_formats)
            else:
                result = self.process_local_video(video_file_or_url, save_txt=save_formats)

            video_content = result.video

            # Generate and save subtitles
            if save_formats:
                self._generate_subtitles(video_content, result.transcript)

            # Generate comprehensive analysis
            analysis = self._generate_enhanced_analysis(result.transcript, video_content.title)

            # Update VideoNote with enhanced analysis
            if result and hasattr(result, 'id'):
                result.summary = analysis['summary']
                result.key_points = analysis['key_points']
                result.conclusion = analysis.get('conclusion', '')
                result.save()

                # Save updated notes with conclusion
                self._save_enhanced_notes(result)

            return result

        except Exception as e:
            logger.error(f"Error in video processing with subtitles: {str(e)}")
            if video_content:
                self.cleanup_model_instance(video_content)
            raise

    def _process_video_in_chunks(self, video_content, video_path, save_txt=False):
        """Process video in chunks with timestamps"""
        conversation = None
        video_note = None
        chunks_dir = None
        created_files = []
        transcript_data = {
            'metadata': {
                'title': video_content.title,
                'processed_date': datetime.now().isoformat(),
                'duration': 0
            },
            'segments': []
        }

        try:
            # Make sure video_content is saved first
            if not video_content.id:
                video_content.save()

            chunks_dir = tempfile.mkdtemp()
            chunk_paths = self.chunker.create_chunks(video_path, chunks_dir)
            logger.info(f"Created {len(chunk_paths)} chunks")

            transcript_segments = []
            total_chunks = len(chunk_paths)
            cumulative_duration = 0

            for i, chunk_path in enumerate(chunk_paths):
                logger.info(f"Processing chunk {i + 1}/{total_chunks}")
                audio_path = os.path.join(chunks_dir, f"chunk_{i}.wav")
                created_files.extend([chunk_path, audio_path])

                try:
                    # Convert video chunk to audio
                    ffmpeg_cmd = [
                        'ffmpeg',
                        '-i', chunk_path,
                        '-vn',
                        '-acodec', 'pcm_s16le',
                        '-ar', '16000',
                        '-ac', '1',
                        '-y',
                        audio_path
                    ]
                    subprocess.run(ffmpeg_cmd, check=True, capture_output=True)

                    # Get chunk duration
                    duration_cmd = [
                        'ffprobe',
                        '-v', 'error',
                        '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        chunk_path
                    ]
                    chunk_duration = float(subprocess.check_output(duration_cmd).decode().strip())

                    # Updated Whisper transcription options
                    result = self.model.transcribe(
                        audio_path,
                        task="transcribe",
                        language=None,
                        verbose=False,
                        word_timestamps=True
                    )

                    # Process segments with timestamps
                    if 'segments' in result:
                        for segment in result['segments']:
                            start_time = cumulative_duration + segment.get('start', 0)
                            end_time = cumulative_duration + segment.get('end', 0)

                            start_formatted = self._format_timestamp(start_time)
                            end_formatted = self._format_timestamp(end_time)

                            segment_text = segment.get('text', '').strip()
                            timestamped_text = f"[{start_formatted} - {end_formatted}] {segment_text}"

                            transcript_segments.append(timestamped_text)

                            transcript_data['segments'].append({
                                'start': start_time,
                                'end': end_time,
                                'start_formatted': start_formatted,
                                'end_formatted': end_formatted,
                                'text': segment_text,
                                'words': segment.get('words', []),
                                'duration': end_time - start_time
                            })
                    else:
                        # Fallback if segments are not available
                        text = result.get('text', '').strip()
                        if text:
                            start_formatted = self._format_timestamp(cumulative_duration)
                            end_formatted = self._format_timestamp(cumulative_duration + chunk_duration)
                            timestamped_text = f"[{start_formatted} - {end_formatted}] {text}"

                            transcript_segments.append(timestamped_text)
                            transcript_data['segments'].append({
                                'start': cumulative_duration,
                                'end': cumulative_duration + chunk_duration,
                                'start_formatted': start_formatted,
                                'end_formatted': end_formatted,
                                'text': text,
                                'duration': chunk_duration
                            })

                    cumulative_duration += chunk_duration
                    logger.debug(f"Transcribed chunk {i + 1}/{total_chunks}")

                finally:
                    self.safe_delete_file(audio_path)
                    self.safe_delete_file(chunk_path)
                    created_files = [f for f in created_files if f not in [audio_path, chunk_path]]

            # Update transcript data with final duration
            transcript_data['metadata']['duration'] = cumulative_duration
            complete_transcript = '\n'.join(segment for segment in transcript_segments if segment.strip())

            # Save transcript files if requested
            if save_txt:
                self._save_transcript_to_file(video_content, complete_transcript, transcript_data)

            try:
                # Create and save conversation
                conversation = Conversation.objects.create(
                    user=self.user,
                    title=f"Notes: {video_content.title}"
                )
                conversation.save()

                # Create and save video note
                video_note = VideoNote.objects.create(
                    video=video_content,
                    transcript=complete_transcript,
                    conversation=conversation,
                    summary="",
                    key_points=[]
                )
                video_note.save()

                # Extract timestamp data for analysis
                timestamp_data = self._extract_timestamp_data(complete_transcript)

                # Generate enhanced analysis
                analysis = self._generate_enhanced_analysis(video_note.transcript, video_content.title)

                # Update video note with analysis results
                video_note.summary = analysis['summary']
                video_note.key_points = analysis['key_points']
                video_note.save()

                # Save all notes including transcript, summary, key points, and conclusion
                self._save_enhanced_notes(video_note, analysis.get('conclusion'))

                logger.info(f"Successfully processed video: {video_content.title}")
                return video_note

            except Exception as e:
                logger.error(f"Error in video processing: {str(e)}")
                # Clean up on error
                if video_note and video_note.id:
                    self.cleanup_model_instance(video_note)
                if conversation and conversation.id:
                    Message.objects.filter(conversation=conversation).delete()
                    self.cleanup_model_instance(conversation)
                raise

        except Exception as e:
            logger.error(f"Error in chunk processing: {str(e)}")
            if video_content and video_content.id:
                self.cleanup_model_instance(video_content)
            raise

        finally:
            # Clean up any remaining files
            for file_path in created_files:
                self.safe_delete_file(file_path)
            if chunks_dir and os.path.exists(chunks_dir):
                self.safe_delete_dir(chunks_dir)

    def _extract_timestamp_data(self, transcript):
        """Extract and analyze timestamp information from transcript"""
        timestamp_data = {
            'segments': [],
            'total_duration': 0,
            'speaker_times': {},
            'topic_segments': []
        }

        # Extract timestamp patterns and associated text
        pattern = r'\[(\d{2}:\d{2}:\d{2}) - (\d{2}:\d{2}:\d{2})\] (.*?)(?=\[|$)'
        matches = re.finditer(pattern, transcript, re.DOTALL)

        for match in matches:
            start_time = self._timestamp_to_seconds(match.group(1))
            end_time = self._timestamp_to_seconds(match.group(2))
            text = match.group(3).strip()

            segment = {
                'start': start_time,
                'end': end_time,
                'duration': end_time - start_time,
                'text': text,
                'start_formatted': match.group(1),
                'end_formatted': match.group(2)
            }

            # Try to identify speaker if format "Speaker: text"
            speaker_match = re.match(r'^([^:]+):\s*(.*)', text)
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                segment['speaker'] = speaker
                # Update speaker times
                if speaker not in timestamp_data['speaker_times']:
                    timestamp_data['speaker_times'][speaker] = 0
                timestamp_data['speaker_times'][speaker] += segment['duration']

            timestamp_data['segments'].append(segment)

        if timestamp_data['segments']:
            timestamp_data['total_duration'] = timestamp_data['segments'][-1]['end']

        return timestamp_data

    def _format_timestamp(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _timestamp_to_seconds(self, timestamp):
        """Convert HH:MM:SS to seconds"""
        h, m, s = map(int, timestamp.split(':'))
        return h * 3600 + m * 60 + s

    def cleanup_model_instance(self, instance):
        """Clean up model instance and related files"""
        try:
            if not instance or not instance.id:
                return

            if hasattr(instance, 'video_file') and instance.video_file:
                try:
                    instance.video_file.delete(save=False)
                except Exception as e:
                    logger.error(f"Error deleting video file: {str(e)}")

            if isinstance(instance, VideoContent):
                # Clean up transcript files
                for field in ['transcript_txt_path', 'transcript_json_path',
                              'transcript_srt_path', 'transcript_vtt_path']:
                    if hasattr(instance, field) and getattr(instance, field):
                        self.safe_delete_file(getattr(instance, field))

                # Clean up related VideoNote if exists
                try:
                    if hasattr(instance, 'video_note') and instance.video_note and instance.video_note.id:
                        self.cleanup_model_instance(instance.video_note)
                except Exception as e:
                    logger.error(f"Error cleaning up VideoNote: {str(e)}")

            elif isinstance(instance, VideoNote):
                # Clean up related conversation and messages
                try:
                    if instance.conversation and instance.conversation.id:
                        Message.objects.filter(conversation=instance.conversation).delete()
                        instance.conversation.delete()
                except Exception as e:
                    logger.error(f"Error cleaning up conversation: {str(e)}")

            # Delete the instance itself if it exists in the database
            try:
                if instance.id:
                    instance.delete()
                    logger.info(f"Cleaned up {instance.__class__.__name__} instance and related files")
            except Exception as e:
                logger.error(f"Error deleting instance: {str(e)}")

        except Exception as e:
            logger.error(f"Error cleaning up instance: {str(e)}")

    def _save_enhanced_notes(self, video_note, conclusion=None):
        """Save enhanced notes including conclusion"""
        try:
            Message.objects.filter(conversation=video_note.conversation).delete()

            # Save transcript
            if video_note.transcript:
                transcript_content = TextContent.objects.create(
                    text=f"Video: {video_note.video.title}\n"
                         f"Duration: {self._format_timestamp(video_note.video.duration)}\n"
                         f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                         f"Transcript with Timestamps:\n\n{video_note.transcript}"
                )
                Message.objects.create(
                    conversation=video_note.conversation,
                    content_type=ContentType.objects.get_for_model(TextContent),
                    object_id=transcript_content.id,
                    is_user=False
                )

            # Save summary
            if video_note.summary:
                summary_content = TextContent.objects.create(
                    text=f"Summary:\n\n{video_note.summary}"
                )
                Message.objects.create(
                    conversation=video_note.conversation,
                    content_type=ContentType.objects.get_for_model(TextContent),
                    object_id=summary_content.id,
                    is_user=False
                )

            # Save enhanced key points
            if video_note.key_points:
                points_text = []
                for point in video_note.key_points:
                    if isinstance(point, str):
                        points_text.append(f"• {point}")
                    elif isinstance(point, dict):
                        timestamp = f"[{point.get('timestamp', 'N/A')}] " if point.get('timestamp') else ""
                        category = f"[{point.get('category', 'General')}] " if point.get('category') else ""
                        text = point.get('text', '')
                        points_text.append(f"• {timestamp}{category}{text}")

                if points_text:
                    points_content = TextContent.objects.create(
                        text="Key Points:\n\n" + "\n".join(points_text)
                    )
                    Message.objects.create(
                        conversation=video_note.conversation,
                        content_type=ContentType.objects.get_for_model(TextContent),
                        object_id=points_content.id,
                        is_user=False
                    )

            # Save conclusion as a separate message
            if conclusion:
                conclusion_content = TextContent.objects.create(
                    text=f"Conclusion:\n\n{conclusion}"
                )
                Message.objects.create(
                    conversation=video_note.conversation,
                    content_type=ContentType.objects.get_for_model(TextContent),
                    object_id=conclusion_content.id,
                    is_user=False
                )

        except Exception as e:
            logger.error(f"Error saving enhanced notes: {str(e)}")
            Message.objects.filter(conversation=video_note.conversation).delete()
            raise

    def _generate_subtitles(self, video_content, transcript):
        """Generate subtitles in multiple formats"""
        try:
            transcript_data = self._parse_transcript_for_subtitles(transcript)
            subtitle_paths = self.transcript_downloader.generate_transcript_formats(
                video_content, transcript_data)

            video_content.subtitle_srt_path = subtitle_paths.get('srt')
            video_content.subtitle_vtt_path = subtitle_paths.get('vtt')
            video_content.save()

            return subtitle_paths

        except Exception as e:
            logger.error(f"Error generating subtitles: {str(e)}")
            raise

    def _parse_transcript_for_subtitles(self, transcript):
        """Parse transcript text into structured data for subtitle generation"""
        pattern = r'\[(\d{2}:\d{2}:\d{2}) - (\d{2}:\d{2}:\d{2})\] (.*?)(?=\[|$)'
        matches = re.finditer(pattern, transcript, re.DOTALL)

        transcript_data = {
            'metadata': {
                'processed_date': datetime.now().isoformat(),
            },
            'segments': []
        }

        for match in matches:
            segment = {
                'start_formatted': match.group(1),
                'end_formatted': match.group(2),
                'start': self._timestamp_to_seconds(match.group(1)),
                'end': self._timestamp_to_seconds(match.group(2)),
                'text': match.group(3).strip()
            }
            transcript_data['segments'].append(segment)

        return transcript_data

    def _generate_enhanced_analysis(self, transcript, title):
        """Generate enhanced analysis including conclusion"""
        try:
            # Get basic analysis
            analysis = self._generate_analysis(transcript, title)

            # Add conclusion
            conclusion = self._generate_conclusion(analysis, transcript)
            analysis['conclusion'] = conclusion

            # Enhance key points with timestamps and categories
            enhanced_points = self._enhance_key_points(analysis['key_points'], transcript)
            analysis['key_points'] = enhanced_points

            return analysis

        except Exception as e:
            logger.error(f"Error generating enhanced analysis: {str(e)}")
            return self._generate_fallback_enhanced_analysis(transcript)

    def _generate_analysis(self, transcript, title):
        """Generate analysis using AI service"""
        try:
            clean_transcript = self._clean_transcript_for_analysis(transcript)
            timestamp_data = self._extract_timestamp_data(transcript)

            perplexity_settings = settings.AI_SERVICES.get('perplexity')
            if not perplexity_settings:
                return self._generate_fallback_analysis(clean_transcript, timestamp_data)

            client = OpenAI(
                api_key=perplexity_settings['api_key'],
                base_url="https://api.perplexity.ai"
            )

            prompt = (
                f"Analyze this video transcript titled \"{title}\".\n\n"
                f"Transcript:\n{transcript}\n\n"
                f"Provide a comprehensive analysis including:\n"
                f"1. A clear 2-3 paragraph summary\n"
                f"2. 5-7 key points with timestamps\n"
                f"3. Analysis of time distribution\n"
                f"4. Notable quotes or moments\n"
                f"Make it specific and insightful."
            )

            response = client.chat.completions.create(
                model=perplexity_settings.get('model', "llama-3-sonar-large-32k-online"),
                messages=[
                    {"role": "system", "content": "You are an expert content analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )

            if response and response.choices and response.choices[0].message:
                return self._parse_analysis_response(response.choices[0].message.content, timestamp_data)
            return self._generate_fallback_analysis(clean_transcript, timestamp_data)

        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            return self._generate_fallback_analysis(transcript, None)

    def _generate_conclusion(self, analysis, transcript):
        """Generate a conclusion based on analysis and transcript"""
        try:
            perplexity_settings = settings.AI_SERVICES.get('perplexity')
            if not perplexity_settings:
                return self._generate_fallback_conclusion(analysis)

            client = OpenAI(
                api_key=perplexity_settings['api_key'],
                base_url="https://api.perplexity.ai"
            )

            prompt = (
                f"Based on this analysis and transcript, generate a thoughtful conclusion that:\n"
                f"1. Synthesizes the main themes\n"
                f"2. Highlights key implications\n"
                f"3. Suggests potential next steps\n\n"
                f"Summary: {analysis['summary']}\n\n"
                f"Key Points: {', '.join(str(p) for p in analysis['key_points'])}\n\n"
                f"Beginning and end of transcript: "
                f"{transcript[:500]}... {transcript[-500:]}"
            )

            response = client.chat.completions.create(
                model=perplexity_settings.get('model', "llama-3-sonar-large-32k-online"),
                messages=[
                    {"role": "system", "content": "Generate a concise, insightful conclusion."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            if response and response.choices and response.choices[0].message:
                return response.choices[0].message.content
            return self._generate_fallback_conclusion(analysis)

        except Exception as e:
            logger.error(f"Error generating conclusion: {str(e)}")
            return self._generate_fallback_conclusion(analysis)

    def _enhance_key_points(self, key_points, transcript):
        """Enhance key points with timestamps and categories"""
        enhanced_points = []

        try:
            timestamp_data = self._extract_timestamp_data(transcript)

            for point in key_points:
                matching_segment = self._find_matching_segment(point, timestamp_data['segments'])
                category = self._categorize_key_point(point)

                enhanced_point = {
                    'text': point,
                    'category': category,
                    'timestamp': matching_segment['start_formatted'] if matching_segment else None,
                    'duration': matching_segment['duration'] if matching_segment else None
                }

                enhanced_points.append(enhanced_point)

            return enhanced_points

        except Exception as e:
            logger.error(f"Error enhancing key points: {str(e)}")
            return [{'text': point, 'category': 'general'} for point in key_points]

    def _save_enhanced_notes(self, video_note, conclusion=None):
        """Save enhanced notes including conclusion"""
        try:
            Message.objects.filter(conversation=video_note.conversation).delete()

            # Save transcript
            if video_note.transcript:
                transcript_content = TextContent.objects.create(
                    text=f"Video: {video_note.video.title}\n"
                         f"Duration: {self._format_timestamp(video_note.video.duration)}\n"
                         f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                         f"Transcript with Timestamps:\n\n{video_note.transcript}"
                )
                Message.objects.create(
                    conversation=video_note.conversation,
                    content_type=ContentType.objects.get_for_model(TextContent),
                    object_id=transcript_content.id,
                    is_user=False
                )

            # Save summary
            if video_note.summary:
                summary_content = TextContent.objects.create(
                    text=f"Summary:\n\n{video_note.summary}"
                )
                Message.objects.create(
                    conversation=video_note.conversation,
                    content_type=ContentType.objects.get_for_model(TextContent),
                    object_id=summary_content.id,
                    is_user=False
                )

            # Save enhanced key points with proper error handling
            if video_note.key_points:
                try:
                    points_text = []
                    for point in video_note.key_points:
                        if isinstance(point, str):
                            points_text.append(f"• {point}")
                        elif isinstance(point, dict):
                            timestamp = f"[{point.get('timestamp', 'N/A')}] " if point.get('timestamp') else ""
                            category = f"[{point.get('category', 'General')}] " if point.get('category') else ""
                            text = point.get('text', '')
                            points_text.append(f"• {timestamp}{category}{text}")

                    if points_text:  # Only create if we have valid points
                        points_content = TextContent.objects.create(
                            text="Key Points:\n\n" + "\n".join(points_text)
                        )
                        Message.objects.create(
                            conversation=video_note.conversation,
                            content_type=ContentType.objects.get_for_model(TextContent),
                            object_id=points_content.id,
                            is_user=False
                        )
                except Exception as e:
                    logger.error(f"Error formatting key points: {str(e)}")
                    # Fallback to simple format if there's an error
                    simple_points = [f"• {str(point)}" for point in video_note.key_points if point]
                    if simple_points:
                        points_content = TextContent.objects.create(
                            text="Key Points:\n\n" + "\n".join(simple_points)
                        )
                        Message.objects.create(
                            conversation=video_note.conversation,
                            content_type=ContentType.objects.get_for_model(TextContent),
                            object_id=points_content.id,
                            is_user=False
                        )

            # Save conclusion
            if conclusion:  # Changed to use the passed conclusion parameter
                conclusion_content = TextContent.objects.create(
                    text=f"Conclusion:\n\n{conclusion}"
                )
                Message.objects.create(
                    conversation=video_note.conversation,
                    content_type=ContentType.objects.get_for_model(TextContent),
                    object_id=conclusion_content.id,
                    is_user=False
                )

        except Exception as e:
            logger.error(f"Error saving enhanced notes: {str(e)}")
            Message.objects.filter(conversation=video_note.conversation).delete()
            raise

    def _timestamp_to_seconds(self, timestamp):
        """Convert HH:MM:SS to seconds"""
        h, m, s = map(int, timestamp.split(':'))
        return h * 3600 + m * 60 + s

    def _format_timestamp(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _clean_transcript_for_analysis(self, transcript):
        """Remove timestamps and clean transcript for analysis"""
        clean_text = re.sub(r'\[\d{2}:\d{2}:\d{2} - \d{2}:\d{2}:\d{2}\]', '', transcript)
        return ' '.join(clean_text.split())

    def _categorize_key_point(self, point):
        """Categorize key point based on content"""
        if isinstance(point, dict):
            point = point['text']

        point_lower = point.lower()
        categories = {
            'definition': ['define', 'means', 'refers to', 'is a', 'are the'],
            'example': ['example', 'instance', 'such as', 'like'],
            'comparison': ['versus', 'compared to', 'whereas', 'while'],
            'process': ['step', 'process', 'procedure', 'method'],
            'impact': ['effect', 'impact', 'influence', 'result'],
            'conclusion': ['therefore', 'thus', 'conclude', 'summary']
        }

        for category, keywords in categories.items():
            if any(keyword in point_lower for keyword in keywords):
                return category

        return 'general'

    def _generate_fallback_analysis(self, transcript, timestamp_data=None):
        """Generate basic analysis when API fails"""
        logger.info("Generating fallback analysis")

        try:
            analysis = {
                'summary': '',
                'key_points': [],
                'speaker_analysis': {},
                'time_distribution': {}
            }

            if timestamp_data:
                # Generate basic summary with timing information
                total_duration = timestamp_data['total_duration']
                segment_count = len(timestamp_data['segments'])

                analysis['summary'] = (
                    f"This video is {self._format_timestamp(total_duration)} long and contains "
                    f"{segment_count} segments of content. The transcript provides a detailed "
                    "record of the spoken content with timestamps."
                )

                # Extract key segments based on duration
                significant_segments = sorted(
                    timestamp_data['segments'],
                    key=lambda x: x['duration'],
                    reverse=True
                )[:5]  # Get top 5 longest segments

                # Generate key points from significant segments
                for segment in significant_segments:
                    point = (
                        f"[{segment['start_formatted']} - {segment['end_formatted']}] "
                        f"{segment['text'][:100]}..."
                    )
                    analysis['key_points'].append(point)

                # Add speaker information if available
                if timestamp_data.get('speaker_times'):
                    speaker_info = []
                    for speaker, duration in timestamp_data['speaker_times'].items():
                        percentage = (duration / total_duration) * 100
                        speaker_info.append(
                            f"{speaker}: {self._format_timestamp(duration)} "
                            f"({percentage:.1f}% of total time)"
                        )
                    analysis['speaker_analysis'] = {
                        'total_speakers': len(timestamp_data['speaker_times']),
                        'speaker_times': speaker_info
                    }

            else:
                # Fallback without timestamp data
                # Split transcript into sentences and create basic summary
                clean_transcript = self._clean_transcript_for_analysis(transcript)
                sentences = [s.strip() for s in clean_transcript.split('.') if s.strip()]

                if sentences:
                    # Take first 3 sentences for summary
                    analysis['summary'] = '. '.join(sentences[:3]) + '.'

                    # Take some sentences for key points
                    for i, sentence in enumerate(sentences[:5], 1):
                        analysis['key_points'].append(f"Point {i}: {sentence}")
                else:
                    analysis['summary'] = "Transcript analysis is not available."
                    analysis['key_points'] = ["Please review the transcript for key points."]

            return analysis

        except Exception as e:
            logger.error(f"Error generating fallback analysis: {str(e)}")
            return {
                'summary': "A transcript of the video is provided above. Please review it for complete information.",
                'key_points': ["Please review the transcript for key points."],
                'speaker_analysis': {},
                'time_distribution': {}
            }

    def _generate_fallback_enhanced_analysis(self, transcript):
        """Generate fallback analysis with basic conclusion"""
        try:
            # Get basic analysis
            analysis = self._generate_fallback_analysis(transcript, None)

            # Add basic conclusion
            analysis['conclusion'] = self._generate_fallback_conclusion(analysis)

            # Add basic categories to key points
            enhanced_points = []
            for i, point in enumerate(analysis['key_points'], 1):
                enhanced_point = {
                    'text': point,
                    'category': 'general',
                    'timestamp': None,
                    'duration': None
                }
                enhanced_points.append(enhanced_point)

            analysis['key_points'] = enhanced_points

            return analysis

        except Exception as e:
            logger.error(f"Error generating fallback enhanced analysis: {str(e)}")
            return {
                'summary': "Please review the transcript for complete information.",
                'key_points': [{'text': "Review the transcript for key points.", 'category': 'general'}],
                'conclusion': "Please review the full transcript for detailed content.",
                'speaker_analysis': {},
                'time_distribution': {}
            }

    def _generate_fallback_conclusion(self, analysis):
        """Generate a basic conclusion when API fails"""
        try:
            # Create a basic conclusion based on available information
            conclusion_parts = []

            if analysis.get('summary'):
                conclusion_parts.append(
                    "The content covers several important topics as outlined in the summary above."
                )

            if analysis.get('key_points'):
                point_count = len(analysis['key_points'])
                conclusion_parts.append(
                    f"The analysis identified {point_count} key points worthy of attention."
                )

            if analysis.get('speaker_analysis'):
                speaker_count = analysis['speaker_analysis'].get('total_speakers', 0)
                if speaker_count:
                    conclusion_parts.append(
                        f"The content features input from {speaker_count} distinct speakers."
                    )

            conclusion_parts.append(
                "For a complete understanding of the content, please review the full "
                "transcript and analysis provided above."
            )

            return " ".join(conclusion_parts)

        except Exception as e:
            logger.error(f"Error generating fallback conclusion: {str(e)}")
            return (
                "Based on the analyzed content, the video provides valuable information. "
                "For a complete understanding, please review the full transcript and key points above."
            )

    def _generate_fallback_conclusion(self, analysis):
        """Generate a basic conclusion when API fails"""
        return (
            "Based on the analyzed content, the video provides valuable information "
            "on the discussed topics. For a complete understanding, please review "
            "the full transcript and key points above."
        )

class TranscriptDownloader:
    """Helper class for transcript downloads in various formats"""

    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_transcript_formats(self, video_content, transcript_data):
        """Generate transcripts in multiple formats"""
        try:
            # Create directory for this video's transcripts
            video_dir = os.path.join(self.output_dir, str(video_content.id))
            os.makedirs(video_dir, exist_ok=True)

            formats = {
                'txt': self._generate_plain_text,
                'srt': self._generate_srt,
                'vtt': self._generate_vtt,
                'json': self._generate_json
            }

            file_paths = {}
            for format_type, generator in formats.items():
                file_path = os.path.join(video_dir, f'transcript_{video_content.id}.{format_type}')
                generator(file_path, video_content, transcript_data)
                file_paths[format_type] = file_path

            return file_paths

        except Exception as e:
            logger.error(f"Error generating transcript formats: {str(e)}")
            raise

    def _generate_plain_text(self, file_path, video_content, transcript_data):
        """Generate plain text transcript with timestamps"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"Title: {video_content.title}\n")
                f.write(f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration: {self._format_timestamp(transcript_data['metadata'].get('duration', 0))}\n\n")

                # Write segments
                f.write("Transcript:\n")
                for segment in transcript_data['segments']:
                    timestamp = f"[{segment['start_formatted']} - {segment['end_formatted']}]"
                    f.write(f"{timestamp} {segment['text']}\n")

                # Write analysis if available
                if 'analysis' in transcript_data:
                    f.write("\nAnalysis:\n")
                    if 'summary' in transcript_data['analysis']:
                        f.write("\nSummary:\n")
                        f.write(transcript_data['analysis']['summary'])

                    if 'speaker_analysis' in transcript_data['analysis']:
                        f.write("\n\nSpeaker Analysis:\n")
                        for speaker_info in transcript_data['analysis']['speaker_analysis']:
                            f.write(f"- {speaker_info}\n")

                    if 'key_points' in transcript_data['analysis']:
                        f.write("\nKey Points:\n")
                        for point in transcript_data['analysis']['key_points']:
                            f.write(f"- {point}\n")

        except Exception as e:
            logger.error(f"Error generating plain text transcript: {str(e)}")
            raise

    def _generate_srt(self, file_path, video_content, transcript_data):
        """Generate SRT format transcript"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(transcript_data['segments'], 1):
                    # Convert timestamps to SRT format (HH:MM:SS,mmm)
                    start_time = self._timestamp_to_srt(segment['start'])
                    end_time = self._timestamp_to_srt(segment['end'])

                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text']}\n\n")

        except Exception as e:
            logger.error(f"Error generating SRT transcript: {str(e)}")
            raise

    def _generate_vtt(self, file_path, video_content, transcript_data):
        """Generate WebVTT format transcript"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("WEBVTT\n\n")

                for i, segment in enumerate(transcript_data['segments'], 1):
                    # Convert timestamps to WebVTT format (HH:MM:SS.mmm)
                    start_time = self._timestamp_to_vtt(segment['start'])
                    end_time = self._timestamp_to_vtt(segment['end'])

                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text']}\n\n")

        except Exception as e:
            logger.error(f"Error generating VTT transcript: {str(e)}")
            raise

    def _generate_json(self, file_path, video_content, transcript_data):
        """Generate JSON format transcript with all metadata"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error generating JSON transcript: {str(e)}")
            raise

    def _timestamp_to_srt(self, seconds):
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_remaining = seconds % 60
        milliseconds = int((seconds_remaining - int(seconds_remaining)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds_remaining):02d},{milliseconds:03d}"

    def _timestamp_to_vtt(self, seconds):
        """Convert seconds to WebVTT timestamp format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_remaining = seconds % 60
        milliseconds = int((seconds_remaining - int(seconds_remaining)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds_remaining):02d}.{milliseconds:03d}"

    def _format_timestamp(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"