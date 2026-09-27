import os
import io
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import pypdf

from .models import ResumeAnalysis
from .serializers import ResumeAnalysisSerializer
from ai.service import ai_service
from notifications.models import Notification


class ResumeAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        target_role = request.data.get('target_role', 'Python Developer')
        resume_file = request.FILES.get('resume')
        raw_text_input = request.data.get('resume_text', '')

        extracted_text = ""
        file_name = "Text-Input"

        if resume_file:
            file_name = os.path.basename(resume_file.name)
            # Validate extension
            if not file_name.lower().endswith('.pdf'):
                return Response(
                    {'error': 'Invalid file format. Please upload a valid PDF document.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate size (Max 5MB)
            if resume_file.size > 5 * 1024 * 1024:
                return Response(
                    {'error': 'File size exceeds limit of 5MB. Please upload a smaller file.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                reader = pypdf.PdfReader(io.BytesIO(resume_file.read()))
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            except Exception as e:
                return Response(
                    {'error': f'Failed to parse PDF document: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif raw_text_input:
            extracted_text = raw_text_input
        else:
            return Response(
                {'error': 'Please provide either a PDF resume file or resume text.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not extracted_text.strip():
            return Response(
                {'error': 'Could not extract text from the provided PDF. Please ensure it is not an image-only scanned PDF.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Run AI analysis
        analysis = ai_service.analyze_resume(extracted_text, target_role=target_role)

        resume_record = ResumeAnalysis.objects.create(
            student=request.user,
            file_name=file_name,
            target_role=target_role,
            raw_text=extracted_text[:10000],  # store first 10k chars
            detected_skills=analysis.get('detected_skills', []),
            missing_skills=analysis.get('missing_skills', []),
            match_percentage=analysis.get('match_percentage', 0.0),
            education_detected=analysis.get('education_detected', []),
            projects_detected=analysis.get('projects_detected', []),
            experience_detected=analysis.get('experience_detected', []),
            tools_detected=analysis.get('tools_detected', []),
            recommended_learning_path=analysis.get('recommended_learning_path', [])
        )

        # Notify student
        Notification.objects.create(
            user=request.user,
            title="Resume Gap Analysis Completed",
            message=f"Your resume match for '{target_role}' is {resume_record.match_percentage}%. Check out recommended skills!",
            notification_type='system',
            link=f"/resume-analyzer"
        )

        return Response(
            ResumeAnalysisSerializer(resume_record).data,
            status=status.HTTP_201_CREATED
        )


class ResumeHistoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResumeAnalysisSerializer

    def get_queryset(self):
        return ResumeAnalysis.objects.filter(student=self.request.user).order_by('-created_at')


class ResumeDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResumeAnalysisSerializer

    def get_queryset(self):
        return ResumeAnalysis.objects.filter(student=self.request.user)
