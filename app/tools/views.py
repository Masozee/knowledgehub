# Python standard library imports
import logging
import anthropic
# Django imports
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

# Third-party imports
import openai
import requests

# Local imports
from .models import *

logger = logging.getLogger(__name__)

def test_logging(request):
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    return HttpResponse("Logging test complete. Check your logs.")


openai.api_key = settings.OPENAI_API_KEY


@login_required
def chat_list(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')

    # Prepare conversation data with UUID
    conversation_data = [
        {
            'uuid': str(conv.uuid),
            'title': conv.title,
            'created_at': conv.created_at,
            'updated_at': conv.updated_at,
            'is_cleared': conv.is_cleared,
            'is_deleted': conv.is_deleted,
            'full_path': conv.full_path,  # Assuming you've added the full_path property to your model
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

    context = {
        'current_chat': conversation,
        'messages': messages,
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

    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    # Save user message
    Message.objects.create(conversation=conversation, content=user_message, is_user=True)

    # Generate title if it's the first message
    if conversation.messages.count() == 1:
        new_title = generate_title(user_message, ai_service)
        conversation.update_title(new_title)

    # Get conversation history
    messages = conversation.messages.order_by('timestamp')
    history = [{"role": "human" if msg.is_user else "assistant", "content": msg.content} for msg in messages]

    # Call appropriate AI service
    try:
        if ai_service == 'claude':
            ai_response = call_claude_api(history, user_message)
        elif ai_service == 'openai':
            ai_response = call_openai_api(history, user_message)
        elif ai_service == 'perplexity':
            ai_response = call_perplexity_api(history, user_message)
        else:
            return JsonResponse({'error': 'Invalid AI service'}, status=400)

        if ai_response:
            # Save AI response
            Message.objects.create(conversation=conversation, content=ai_response, is_user=False, ai_service=ai_service)
            conversation.save()  # Update the 'updated_at' timestamp
            return JsonResponse({'message': ai_response, 'title': conversation.title})
        else:
            return JsonResponse({'error': f'Failed to get response from {ai_service}'}, status=500)
    except Exception as e:
        logger.exception(f"Error in send_message view: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


def call_claude_api(history, user_message):
    try:
        anthropic_settings = settings.AI_SERVICES['anthropic']
        client = anthropic.Anthropic(api_key=anthropic_settings['api_key'])

        # Convert history to the format expected by the Claude API
        formatted_messages = []
        for msg in history:
            formatted_messages.append({
                "role": "user" if msg["role"] == "human" else "assistant",
                "content": [{"type": "text", "text": msg["content"]}]
            })

        # Add the new user message
        formatted_messages.append({
            "role": "user",
            "content": [{"type": "text", "text": user_message}]
        })

        response = client.messages.create(
            model=anthropic_settings['model'],
            max_tokens=anthropic_settings['max_tokens'],
            temperature=0,  # You can adjust this or make it configurable
            messages=formatted_messages
        )

        return response.content[0].text
    except Exception as e:
        logger.exception(f"Error calling Claude API: {str(e)}")
        return None


def call_openai_api(history, user_message):
    try:
        openai_settings = settings.AI_SERVICES['openai']
        openai.api_key = openai_settings['api_key']
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        for msg in history:
            messages.append({"role": "user" if msg["role"] == "human" else "assistant", "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        response = openai.ChatCompletion.create(
            model=openai_settings['model'],
            messages=messages,
            max_tokens=openai_settings['max_tokens'],
            temperature=openai_settings['temperature'],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception(f"Error calling OpenAI API: {str(e)}")
        return None


def call_perplexity_api(history, user_message):
    try:
        perplexity_settings = settings.AI_SERVICES['perplexity']
        url = "https://api.perplexity.ai/chat/completions"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {perplexity_settings['api_key']}"
        }

        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        for msg in history:
            messages.append({"role": "user" if msg["role"] == "human" else "assistant", "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": perplexity_settings['model'],
            "messages": messages,
            "max_tokens": perplexity_settings['max_tokens'],
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.exception(f"Error calling Perplexity API: {str(e)}")
        return None


def generate_title(first_message, ai_service):
    prompt = f"Generate a short, descriptive title (max 5 words) for a conversation that starts with: '{first_message}'"

    try:
        if ai_service == 'openai':
            openai_settings = settings.AI_SERVICES['openai']
            openai.api_key = openai_settings['api_key']
            response = openai.Completion.create(
                engine=openai_settings['model'],
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
            # Implement Perplexity API call here
            # This is a placeholder, you'll need to replace it with actual Perplexity API call
            return f"Conversation about {first_message[:20]}..."

    except Exception as e:
        logger.exception(f"Error generating title with {ai_service}: {str(e)}")

    # Fallback to a simple title if AI generation fails
    return f"{first_message[:20]}..."

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