from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from .models import Conversation, Message, TextContent, CodeContent, ImageContent
import logging
import re
import requests
from django.core.files.base import ContentFile
import anthropic
from openai import OpenAI

logger = logging.getLogger(__name__)


# AI service functions
def call_claude_api(history, user_message):
    try:
        anthropic_settings = settings.AI_SERVICES['anthropic']
        client = anthropic.Anthropic(api_key=anthropic_settings['api_key'])

        formatted_messages = []
        for msg in history:
            formatted_messages.append({
                "role": "user" if msg["role"] == "human" else "assistant",
                "content": [{"type": "text", "text": msg["content"]}]
            })

        formatted_messages.append({
            "role": "user",
            "content": [{"type": "text", "text": user_message}]
        })

        response = client.messages.create(
            model=anthropic_settings['model'],
            max_tokens=anthropic_settings['max_tokens'],
            temperature=0,
            messages=formatted_messages
        )

        return analyze_response(response.content[0].text)
    except Exception as e:
        logger.exception(f"Error calling Claude API: {str(e)}")
        return None


def call_openai_api(history, user_message):
    try:
        openai_settings = settings.AI_SERVICES['openai']
        client = OpenAI(api_key=openai_settings['api_key'])

        # Check if the user is requesting an image
        if "generate image" in user_message.lower():
            response = client.images.generate(
                model="dall-e-3",
                prompt=user_message,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            return {
                'type': 'image',
                'content': image_url,
                'caption': user_message
            }
        else:
            # Existing text completion logic
            messages = [{"role": "system", "content": "You are a helpful assistant."}]
            for msg in history:
                messages.append({"role": "user" if msg["role"] == "human" else "assistant", "content": msg["content"]})
            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=openai_settings['model'],
                messages=messages,
                max_tokens=openai_settings['max_tokens'],
                temperature=openai_settings['temperature'],
            )
            return {
                'type': 'text',
                'content': response.choices[0].message.content.strip()
            }
    except Exception as e:
        logger.exception(f"Error calling OpenAI API: {str(e)}")
        return None


def call_perplexity_api(history, user_message):
    try:
        perplexity_settings = settings.AI_SERVICES['perplexity']
        client = OpenAI(
            api_key=perplexity_settings['api_key'],
            base_url="https://api.perplexity.ai"
        )

        messages = [{"role": "system", "content": "You are a helpful assistant."}]

        if history:
            if history[0]['role'] != 'human':
                messages.append({"role": "user", "content": "Hello"})

            for msg in history:
                role = "user" if msg['role'] == 'human' else "assistant"
                messages.append({"role": role, "content": msg['content']})

        if len(messages) % 2 == 0:
            messages.append({"role": "assistant", "content": "I understand. How can I assist you further?"})

        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=perplexity_settings['model'],
            messages=messages,
            max_tokens=perplexity_settings.get('max_tokens', 1000),
        )
        return analyze_response(response.choices[0].message.content.strip())
    except Exception as e:
        logger.exception(f"Error calling Perplexity API: {str(e)}")
        return None


def analyze_response(response):
    if response.startswith('http') and any(ext in response for ext in ['.png', '.jpg', '.jpeg', '.gif']):
        return {
            'type': 'image',
            'content': response,
            'caption': ''
        }

    code_pattern = r'```[\s\S]*?```'
    code_blocks = re.findall(code_pattern, response)

    if code_blocks:
        code = code_blocks[0].strip('`').strip()
        language = code.split('\n')[0] if '\n' in code else ''
        code = code[len(language):].strip() if language else code

        return {
            'type': 'code',
            'content': code,
            'language': language
        }

    return {
        'type': 'text',
        'content': response
    }


def process_ai_response(ai_response):
    if ai_response['type'] == 'text':
        content_object = TextContent.objects.create(text=ai_response['content'])
        return TextContent, content_object
    elif ai_response['type'] == 'code':
        content_object = CodeContent.objects.create(code=ai_response['content'], language=ai_response['language'])
        return CodeContent, content_object
    elif ai_response['type'] == 'image':
        response = requests.get(ai_response['content'])
        if response.status_code == 200:
            image_name = ai_response['content'].split('/')[-1]
            image_content = ContentFile(response.content)
            content_object = ImageContent()
            content_object.image.save(image_name, image_content, save=True)
            content_object.caption = ai_response['caption']
            content_object.save()
            return ImageContent, content_object
    else:
        raise ValueError(f"Unknown content type: {ai_response['type']}")


@login_required
@require_POST
def send_message(request, conversation_uuid):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    conversation = get_object_or_404(Conversation, uuid=conversation_uuid, user=request.user)
    user_message = request.POST.get('message')
    ai_service = request.POST.get('ai_service', 'claude')

    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    try:
        # Save user message
        text_content = TextContent.objects.create(text=user_message)
        Message.objects.create(
            conversation=conversation,
            content_type=ContentType.objects.get_for_model(TextContent),
            object_id=text_content.id,
            is_user=True
        )

        # Generate title if it's the first message
        if conversation.messages.count() == 1:
            new_title = generate_title(user_message, ai_service)
            conversation.update_title(new_title)

        # Get conversation history
        messages = conversation.messages.order_by('timestamp')
        history = []
        for msg in messages:
            content = msg.content_object
            if isinstance(content, TextContent):
                history.append({"role": "human" if msg.is_user else "assistant", "content": content.text})
            elif isinstance(content, CodeContent):
                history.append({"role": "human" if msg.is_user else "assistant",
                                "content": f"```{content.language}\n{content.code}\n```"})
            elif isinstance(content, ImageContent):
                history.append(
                    {"role": "human" if msg.is_user else "assistant", "content": f"[Image: {content.caption}]"})

        # Call appropriate AI service
        ai_response = None
        if ai_service == 'claude':
            ai_response = call_claude_api(history, user_message)
        elif ai_service == 'openai':
            ai_response = call_openai_api(history, user_message)
        elif ai_service == 'perplexity':
            ai_response = call_perplexity_api(history, user_message)
        else:
            return JsonResponse({'error': 'Invalid AI service'}, status=400)

        if ai_response:
            content_type, content_object = process_ai_response(ai_response)

            Message.objects.create(
                conversation=conversation,
                content_type=ContentType.objects.get_for_model(content_type),
                object_id=content_object.id,
                is_user=False,
                ai_service=ai_service
            )

            conversation.save()  # Update the 'updated_at' timestamp

            response_data = {
                'message': ai_response['content'],
                'title': conversation.title,
                'content_type': ai_response['type'],
            }

            if ai_response['type'] == 'code':
                response_data['language'] = ai_response['language']
            elif ai_response['type'] == 'image':
                response_data['image_url'] = content_object.image.url
                response_data['caption'] = content_object.caption

            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': f'Failed to get response from {ai_service}'}, status=500)

    except Exception as e:
        logger.exception(f"Error in send_message view: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


def generate_title(first_message, ai_service):
    prompt = f"Generate a short, descriptive title (max 5 words) for a conversation that starts with: '{first_message}'"

    try:
        if ai_service == 'openai':
            openai_settings = settings.AI_SERVICES['openai']
            client = OpenAI(api_key=openai_settings['api_key'])
            response = client.completions.create(
                model=openai_settings['model'],
                prompt=prompt,
                max_tokens=10,
                n=1,
                stop=None,
                temperature=openai_settings['temperature'],
            )
            return response.choices[0].text.strip()

        elif ai_service == 'claude':
            anthropic_settings = settings.AI_SERVICES['anthropic']
            client = anthropic.Anthropic(api_key=anthropic_settings['api_key'])
            response = client.completions.create(
                model=anthropic_settings['model'],
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                max_tokens_to_sample=anthropic_settings['max_tokens'],
                temperature=0.7,
            )
            return response.completion.strip()

        elif ai_service == 'perplexity':
            perplexity_settings = settings.AI_SERVICES['perplexity']
            client = OpenAI(
                api_key=perplexity_settings['api_key'],
                base_url="https://api.perplexity.ai"
            )
            response = client.completions.create(
                model=perplexity_settings['model'],
                prompt=prompt,
                max_tokens=10,
                n=1,
                stop=None,
                temperature=0.7,
            )
            return response.choices[0].text.strip()

    except Exception as e:
        logger.exception(f"Error generating title with {ai_service}: {str(e)}")

    # Fallback to a simple title if AI generation fails
    return f"Chat about {first_message[:20]}..."