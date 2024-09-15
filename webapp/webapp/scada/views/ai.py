from django.shortcuts import render, redirect, get_object_or_404

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.views import generic
from django.views import View
from django.http import HttpResponse, JsonResponse

from ..sqlalchemy_setup import get_dbsession
from sqlalchemy.orm import sessionmaker
from ..models.auth_entity import AuthEntity
from ..forms.contact import ContactForm
from ..forms.subscribe import SubscribeForm
from ..forms.ai import AiForm

from transformers import pipeline

# Initialize the AI model
ai_model = pipeline("text-generation", model="gpt2")
# ai_model = pipeline("text-generation", model="EleutherAI/gpt-j-6B")
# Initialize the question-answering pipeline
# ai_model = pipeline(
#     "question-answering", model="distilbert-base-uncased-distilled-squad"
# )
# Use Flan-T5 model
# ai_model = pipeline("text2text-generation", model="google/flan-t5-large")


# =======================================================================================================================
class AiView(View):
    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        ai_form = AiForm(request.POST)
        if ai_form.is_valid():
            comment = ai_form.cleaned_data["comment"].lower()

            # Generate AI response
            try:
                result = ai_model(
                    comment,
                    num_return_sequences=1,  # Generate only 1 output sequence
                    max_new_tokens=1000000,  # Limit output to 100 tokens
                    truncation=True,  # Explicitly enable truncation
                    pad_token_id=ai_model.tokenizer.eos_token_id,  # Set padding token explicitly
                )
                response_text = result[0]["generated_text"]
                # Return the response in JSON format
                return JsonResponse({"success": True, "response_text": response_text})
            except Exception:
                return JsonResponse(
                    {
                        "success": False,
                        "response_text": "Content can't be generated. PLease try again.",
                    }
                )
        else:
            # If the form is not valid, render the form with errors
            template = "scada/main.html"
            ai_form = AiForm(request.POST)
            context = {
                "sign_up_form": ai_form,
            }
            return render(request, template, context)
