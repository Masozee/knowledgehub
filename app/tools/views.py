# Python standard library imports
import logging

# Django imports
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
import json
from django.core.serializers.json import DjangoJSONEncoder

# Local imports
from .models import Conversation, Message, TextContent, CodeContent, ImageContent
from .ai_services import call_claude_api, call_openai_api, call_perplexity_api, process_ai_response, generate_title

logger = logging.getLogger(__name__)

def serialize_message(message):
    content = message.content_object
    serialized = {
        'id': str(message.id),
        'is_user': message.is_user,
        'ai_service': message.ai_service,
        'timestamp': message.timestamp.isoformat(),
    }

    if isinstance(content, TextContent):
        serialized.update({
            'type': 'text',
            'content': content.text,
        })
    elif isinstance(content, CodeContent):
        serialized.update({
            'type': 'code',
            'content': content.code,
            'language': content.language,
        })
    elif isinstance(content, ImageContent):
        serialized.update({
            'type': 'image',
            'content': content.caption,
            'image_url': content.image.url,
        })

    return serialized

def test_logging(request):
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    return HttpResponse("Logging test complete. Check your logs.")

@login_required
def chat_list(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')

    conversation_data = [
        {
            'uuid': str(conv.uuid),
            'title': conv.title,
            'created_at': conv.created_at,
            'updated_at': conv.updated_at,
            'is_cleared': conv.is_cleared,
            'is_deleted': conv.is_deleted,
            'full_path': conv.full_path,
        }
        for conv in conversations
    ]

    context = {
        'conversations': conversation_data,
    }
    return render(request, 'dashboard/chat/index.html', context)

@login_required
def chat_detail(request, conversation_uuid):
    conversation = get_object_or_404(Conversation, uuid=conversation_uuid, user=request.user)
    messages = conversation.messages.order_by('timestamp')
    all_chats = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    ai_services = ['claude', 'openai', 'perplexity']  # Add or remove services as needed

    serialized_messages = [serialize_message(msg) for msg in messages]

    context = {
        'current_chat': conversation,
        'messages': messages,  # Keep the original queryset for template rendering
        'serialized_messages': json.dumps(serialized_messages, cls=DjangoJSONEncoder),
        'all_chats': all_chats,
        'ai_services': ai_services,
    }
    return render(request, 'dashboard/chat/detail.html', context)

@login_required
def new_conversation(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        conversation = Conversation.objects.create(user=request.user)
        return JsonResponse({
            'chat': {
                'uuid': str(conversation.uuid),
                'title': conversation.title,
                'created_at': conversation.created_at.isoformat()
            }
        })
    else:
        conversation = Conversation.objects.create(user=request.user)
        return redirect('tools:chat_detail', conversation_uuid=conversation.uuid)


@login_required
@require_POST
def send_message(request, conversation_uuid):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    conversation = get_object_or_404(Conversation, uuid=conversation_uuid, user=request.user)
    user_message = request.POST.get('message')
    ai_service = request.POST.get('ai_service', 'claude')

    logger.info(f"Attempting to send message using {ai_service} service")

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
            logger.error(f"Invalid AI service: {ai_service}")
            return JsonResponse({'error': 'Invalid AI service'}, status=400)

        if ai_response:
            logger.info(f"Received response from {ai_service}")
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
            logger.error(f"Failed to get response from {ai_service}")
            return JsonResponse({'error': f'Failed to get response from {ai_service}'}, status=500)

    except Exception as e:
        logger.exception(f"Error in send_message view: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

@login_required
def delete_conversation(request, conversation_uuid):
    conversation = get_object_or_404(Conversation, uuid=conversation_uuid, user=request.user)
    conversation.delete_conversation()
    return redirect('tools:chatlist')

@login_required
def clear_conversation(request, conversation_uuid):
    conversation = get_object_or_404(Conversation, uuid=conversation_uuid, user=request.user)
    conversation.clear_chat()
    return redirect('tools:chat_detail', conversation_uuid=conversation.uuid)