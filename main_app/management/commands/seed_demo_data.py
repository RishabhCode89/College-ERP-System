import os
from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from main_app.models import (
    Attendance,
    AttendanceReport,
    Book,
    Course,
    CustomUser,
    FeedbackStaff,
    FeedbackStudent,
    IssuedBook,
    NotificationStaff,
    NotificationStudent,
    Session,
    Staff,
    Student,
    StudentResult,
    Subject,
)


class Command(BaseCommand):
    help = "Seed demo data for staff and student panels"

    def handle(self, *args, **options):
        demo_password = "DemoPass123"
        profile_pic = self._pick_profile_pic()

        session, _ = Session.objects.get_or_create(
            start_year=date(2025, 6, 1),
            end_year=date(2026, 5, 31),
        )

        course_cs, _ = Course.objects.get_or_create(name="Computer Science")
        course_me, _ = Course.objects.get_or_create(name="Mechanical Engineering")

        staff_alex = self._get_or_create_user(
            email="staff.alex@example.com",
            user_type="2",
            first_name="Alex",
            last_name="Khan",
            gender="M",
            address="Block A, Faculty Quarters",
            profile_pic=profile_pic,
            password=demo_password,
        )
        staff_sara = self._get_or_create_user(
            email="staff.sara@example.com",
            user_type="2",
            first_name="Sara",
            last_name="Mehta",
            gender="F",
            address="Block B, Faculty Quarters",
            profile_pic=profile_pic,
            password=demo_password,
        )

        staff_alex.staff.course = course_cs
        staff_alex.staff.save()
        staff_sara.staff.course = course_me
        staff_sara.staff.save()

        student_riya = self._get_or_create_user(
            email="student.riya@example.com",
            user_type="3",
            first_name="Riya",
            last_name="Sharma",
            gender="F",
            address="Hostel 1, Room 203",
            profile_pic=profile_pic,
            password=demo_password,
        )
        student_karan = self._get_or_create_user(
            email="student.karan@example.com",
            user_type="3",
            first_name="Karan",
            last_name="Patel",
            gender="M",
            address="Hostel 2, Room 110",
            profile_pic=profile_pic,
            password=demo_password,
        )

        student_anaya = self._get_or_create_user(
            email="student.anaya@example.com",
            user_type="3",
            first_name="Anaya",
            last_name="Gupta",
            gender="F",
            address="Hostel 3, Room 08",
            profile_pic=profile_pic,
            password=demo_password,
        )
        student_rohan = self._get_or_create_user(
            email="student.rohan@example.com",
            user_type="3",
            first_name="Rohan",
            last_name="Singh",
            gender="M",
            address="Hostel 4, Room 15",
            profile_pic=profile_pic,
            password=demo_password,
        )

        student_riya.student.course = course_cs
        student_riya.student.session = session
        student_riya.student.save()

        student_karan.student.course = course_cs
        student_karan.student.session = session
        student_karan.student.save()

        student_anaya.student.course = course_me
        student_anaya.student.session = session
        student_anaya.student.save()

        student_rohan.student.course = course_me
        student_rohan.student.session = session
        student_rohan.student.save()

        subject_algo, _ = Subject.objects.get_or_create(
            name="Algorithms",
            staff=staff_alex.staff,
            course=course_cs,
        )
        subject_db, _ = Subject.objects.get_or_create(
            name="Databases",
            staff=staff_alex.staff,
            course=course_cs,
        )
        subject_cad, _ = Subject.objects.get_or_create(
            name="CAD Design",
            staff=staff_sara.staff,
            course=course_me,
        )

        self._seed_attendance(session, subject_algo, [student_riya.student, student_karan.student])
        self._seed_attendance(session, subject_db, [student_riya.student, student_karan.student])
        self._seed_attendance(session, subject_cad, [student_anaya.student, student_rohan.student])

        self._seed_results([student_riya.student, student_karan.student], [subject_algo, subject_db])
        self._seed_results([student_anaya.student, student_rohan.student], [subject_cad])

        NotificationStaff.objects.get_or_create(
            staff=staff_alex.staff,
            message="Reminder: Submit internal marks by Friday.",
        )
        NotificationStaff.objects.get_or_create(
            staff=staff_alex.staff,
            message="Timetable update: Lab moved to Room 204.",
        )

        NotificationStudent.objects.get_or_create(
            student=student_riya.student,
            message="Your library book is due in 3 days.",
        )
        NotificationStudent.objects.get_or_create(
            student=student_karan.student,
            message="Attendance updated for Algorithms.",
        )

        FeedbackStaff.objects.get_or_create(
            staff=staff_alex.staff,
            feedback="Need a projector in Lab 2.",
            reply="Approved. Facility will be arranged.",
        )
        FeedbackStudent.objects.get_or_create(
            student=student_riya.student,
            feedback="Canteen timing conflicts with labs.",
            reply="We will review the timing.",
        )

        book_py, _ = Book.objects.get_or_create(
            name="Python Basics",
            author="Arun Rao",
            isbn=100200300,
            category="Programming",
        )
        book_db, _ = Book.objects.get_or_create(
            name="Database Systems",
            author="S. K. Sharma",
            isbn=200300400,
            category="Databases",
        )
        Book.objects.get_or_create(
            name="Algorithms Made Simple",
            author="Neha Verma",
            isbn=300400500,
            category="Algorithms",
        )

        IssuedBook.objects.get_or_create(
            student_id=str(student_riya.student.id),
            isbn=str(book_py.isbn),
        )
        IssuedBook.objects.get_or_create(
            student_id=str(student_karan.student.id),
            isbn=str(book_db.isbn),
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
        self.stdout.write("Login credentials (demo):")
        self.stdout.write("Staff: staff.alex@example.com / DemoPass123")
        self.stdout.write("Student: student.riya@example.com / DemoPass123")

    def _pick_profile_pic(self):
        candidates = [
            "86536394.jpg",
            "86536394_8BIcnKQ.jpg",
            "6298298029391417491.jpg",
            "PhotoshopExtension_Image.png",
        ]
        for name in candidates:
            if os.path.exists(os.path.join(settings.MEDIA_ROOT, name)):
                return name
        return ""

    def _get_or_create_user(self, email, user_type, first_name, last_name, gender, address, profile_pic, password):
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                user_type=user_type,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                address=address,
                profile_pic=profile_pic,
            )
            self._ensure_profile(user)
            return user

        user.user_type = user_type
        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender
        user.address = address
        if profile_pic:
            user.profile_pic = profile_pic
        user.save()
        self._ensure_profile(user)
        return user

    def _ensure_profile(self, user):
        if user.user_type == "2":
            Staff.objects.get_or_create(admin=user)
        elif user.user_type == "3":
            Student.objects.get_or_create(admin=user)

    def _seed_attendance(self, session, subject, students):
        base_date = timezone.localdate() - timedelta(days=7)
        for offset in range(0, 3):
            att_date = base_date + timedelta(days=offset * 2)
            attendance, _ = Attendance.objects.get_or_create(
                session=session,
                subject=subject,
                date=att_date,
            )
            for index, student in enumerate(students):
                status = (index + offset) % 2 == 0
                AttendanceReport.objects.get_or_create(
                    student=student,
                    attendance=attendance,
                    defaults={"status": status},
                )

    def _seed_results(self, students, subjects):
        for student in students:
            for subject in subjects:
                StudentResult.objects.get_or_create(
                    student=student,
                    subject=subject,
                    defaults={"test": 18.0, "exam": 62.0},
                )
