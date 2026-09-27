from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, Skill, StudentProfile


class AuthAndPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')

        self.student_user = User.objects.create_user(
            username='teststudent',
            email='teststudent@example.com',
            password='Password@123',
            role='STUDENT'
        )
        StudentProfile.objects.create(user=self.student_user)

        self.instructor_user = User.objects.create_user(
            username='testinstructor',
            email='testinstructor@example.com',
            password='Password@123',
            role='INSTRUCTOR'
        )

        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='Password@123',
            role='ADMIN',
            is_staff=True,
            is_superuser=True
        )

    def test_student_registration_success(self):
        payload = {
            'username': 'newstudent',
            'email': 'newstudent@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'role': 'STUDENT'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newstudent@example.com').exists())

    def test_duplicate_email_registration_rejected(self):
        payload = {
            'username': 'anotherone',
            'email': 'teststudent@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'role': 'STUDENT'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_login_and_jwt_tokens(self):
        payload = {
            'email': 'teststudent@example.com',
            'password': 'Password@123'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_invalid_login_rejected(self):
        payload = {
            'email': 'teststudent@example.com',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_stats_permission(self):
        stats_url = reverse('admin_stats')

        # Unauthenticated request should fail
        res_unauth = self.client.get(stats_url)
        self.assertEqual(res_unauth.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should be forbidden
        self.client.force_authenticate(user=self.student_user)
        res_student = self.client.get(stats_url)
        self.assertEqual(res_student.status_code, status.HTTP_403_FORBIDDEN)

        # Admin should succeed
        self.client.force_authenticate(user=self.admin_user)
        res_admin = self.client.get(stats_url)
        self.assertEqual(res_admin.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', res_admin.data)

    # =========================================================================
    # ROLE MANAGEMENT & REGISTRATION SECURITY TESTS (TEST 1 - TEST 7)
    # =========================================================================

    def test_1_unauthenticated_public_signup_without_role_creates_student(self):
        """TEST 1: Unauthenticated public signup without a role creates Student."""
        payload = {
            'username': 'norolestudent',
            'email': 'norolestudent@example.com',
            'first_name': 'Normal',
            'last_name': 'Student',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(email='norolestudent@example.com')
        self.assertEqual(created_user.role, 'STUDENT')
        self.assertTrue(hasattr(created_user, 'student_profile'))
        self.assertFalse(hasattr(created_user, 'instructor_profile'))

    def test_2_unauthenticated_signup_with_role_instructor_rejected(self):
        """TEST 2: Unauthenticated signup with role=instructor is rejected with 400."""
        # Test lowercase
        payload_lower = {
            'username': 'fakeinstructor1',
            'email': 'fakeinstructor1@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'role': 'instructor',
        }
        res_lower = self.client.post(self.register_url, payload_lower, format='json')
        self.assertEqual(res_lower.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='fakeinstructor1@example.com').exists())

        # Test uppercase
        payload_upper = {
            'username': 'fakeinstructor2',
            'email': 'fakeinstructor2@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'role': 'INSTRUCTOR',
        }
        res_upper = self.client.post(self.register_url, payload_upper, format='json')
        self.assertEqual(res_upper.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='fakeinstructor2@example.com').exists())

    def test_3_unauthenticated_signup_with_role_admin_rejected(self):
        """TEST 3: Unauthenticated signup with role=admin is rejected with 400."""
        payload = {
            'username': 'fakeadmin',
            'email': 'fakeadmin@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'role': 'ADMIN',
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='fakeadmin@example.com').exists())

    def test_4_normal_student_cannot_create_or_promote_instructor(self):
        """TEST 4: Normal Student cannot create or promote an Instructor."""
        self.client.force_authenticate(user=self.student_user)

        # Attempt to create instructor via admin endpoint
        create_payload = {
            'username': 'studentcreatedinstructor',
            'email': 'studentcreated@example.com',
            'password': 'Password123!',
            'title': 'Unauthorized Instructor',
        }
        res_create = self.client.post('/api/admin/instructors/', create_payload, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_403_FORBIDDEN)

        # Attempt to create via admin users endpoint
        res_users = self.client.post('/api/admin/users/', create_payload, format='json')
        self.assertEqual(res_users.status_code, status.HTTP_403_FORBIDDEN)

        # Attempt to promote self via profile endpoint
        res_profile = self.client.put('/api/auth/profile/', {'role': 'INSTRUCTOR'}, format='json')
        self.assertEqual(res_profile.status_code, status.HTTP_403_FORBIDDEN)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.role, 'STUDENT')

        # Attempt to modify another user via admin user detail
        res_detail = self.client.patch(f'/api/admin/users/{self.student_user.id}/', {'role': 'INSTRUCTOR'}, format='json')
        self.assertEqual(res_detail.status_code, status.HTTP_403_FORBIDDEN)

    def test_5_admin_can_create_instructor(self):
        """TEST 5: Admin can create Instructor."""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'username': 'legitinstructor',
            'email': 'legitinstructor@skillnova.ai',
            'first_name': 'Sarah',
            'last_name': 'Connor',
            'password': 'InstructorSecurePass@123',
            'title': 'Senior Systems Instructor',
            'organization': 'SkillNova Academy',
            'expertise': 'Python, Distributed Systems, Cloud Architecture'
        }
        response = self.client.post('/api/admin/instructors/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='legitinstructor@skillnova.ai').exists())

        created = User.objects.get(email='legitinstructor@skillnova.ai')
        self.assertTrue(created.is_active)
        self.assertTrue(hasattr(created, 'instructor_profile'))
        self.assertEqual(created.instructor_profile.title, 'Senior Systems Instructor')

    def test_5b_admin_create_instructor_with_blank_or_missing_username_succeeds(self):
        """Admin creates instructor with blank username (as submitted by React modal); username auto-generated."""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'first_name': 'Grace',
            'last_name': 'Hopper',
            'username': '',  # Blank username sent by the modal form
            'email': 'grace.hopper@skillnova.ai',
            'password': 'InstructorPassword123!',
            'title': 'Lead Technical Instructor',
            'organization': 'SkillNova Academy',
            'expertise': 'Compilers, Computer Systems'
        }
        response = self.client.post('/api/admin/instructors/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'grace_hopper')
        self.assertEqual(response.data['user']['role'], 'INSTRUCTOR')

        created = User.objects.get(email='grace.hopper@skillnova.ai')
        self.assertTrue(created.check_password('InstructorPassword123!'))
        self.assertNotEqual(created.password, 'InstructorPassword123!')  # Password must be hashed

    def test_5c_admin_create_instructor_duplicate_email_rejected(self):
        """Admin creating an instructor with an existing email returns clear validation error."""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': 'testinstructor@example.com',  # Already exists from setUp
            'password': 'InstructorPassword123!',
        }
        response = self.client.post('/api/admin/instructors/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('An account with this email already exists.', str(response.data['email']))

    def test_5d_admin_create_instructor_handles_username_collision_automatically(self):
        """When multiple instructors have matching email prefixes, username collisions append sequential numbers."""
        self.client.force_authenticate(user=self.admin_user)
        # Create first instructor with email local-part 'dev'
        p1 = {
            'email': 'dev@domain1.com',
            'password': 'Password123!',
        }
        res1 = self.client.post('/api/admin/instructors/', p1, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res1.data['user']['username'], 'dev')

        # Create second instructor with different domain but same local-part 'dev'
        p2 = {
            'email': 'dev@domain2.com',
            'password': 'Password123!',
        }
        res2 = self.client.post('/api/admin/instructors/', p2, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.data['user']['username'], 'dev1')

        # Create third instructor with same prefix
        p3 = {
            'email': 'dev@domain3.com',
            'password': 'Password123!',
        }
        res3 = self.client.post('/api/admin/instructors/', p3, format='json')
        self.assertEqual(res3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res3.data['user']['username'], 'dev2')

    def test_6_created_instructor_can_login(self):
        """TEST 6: Created Instructor can login successfully and receive JWT tokens."""
        # Admin creates instructor
        self.client.force_authenticate(user=self.admin_user)
        create_payload = {
            'username': 'logininstructor',
            'email': 'logininstructor@skillnova.ai',
            'first_name': 'Alan',
            'last_name': 'Turing',
            'password': 'LoginPassword@123',
        }
        res_create = self.client.post('/api/admin/instructors/', create_payload, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)

        # Unauthenticate and log in with the new instructor credentials
        self.client.force_authenticate(user=None)
        login_res = self.client.post(self.login_url, {
            'email': 'logininstructor@skillnova.ai',
            'password': 'LoginPassword@123'
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', login_res.data)
        self.assertIn('access', login_res.data['tokens'])
        self.assertEqual(login_res.data['user']['role'], 'INSTRUCTOR')

    def test_7_existing_instructor_role_and_permissions_continue_working(self):
        """TEST 7: Existing Instructor role and permissions continue working."""
        self.client.force_authenticate(user=self.instructor_user)

        # Instructor can view their profile
        prof_res = self.client.get('/api/auth/profile/')
        self.assertEqual(prof_res.status_code, status.HTTP_200_OK)
        self.assertEqual(prof_res.data['role'], 'INSTRUCTOR')

        # Instructor can view student performance endpoint
        perf_res = self.client.get('/api/instructor/performance/')
        self.assertEqual(perf_res.status_code, status.HTTP_200_OK)

    # =========================================================================
    # ACTIVATION & DEACTIVATION PERSISTENCE TESTS (TEST A - TEST I)
    # =========================================================================

    def test_a_and_b_admin_deactivates_student_and_persists_on_fetch(self):
        """TEST A & B: Admin deactivates Student, db updates, and subsequent fetch shows inactive."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_user_detail', kwargs={'pk': self.student_user.id})

        # TEST A: Admin deactivates student
        res = self.client.patch(url, {'is_active': False}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['is_active'])

        # Database verification
        self.student_user.refresh_from_db()
        self.assertFalse(self.student_user.is_active)

        # TEST B: Fetch users again (simulating page refresh)
        list_res = self.client.get(reverse('admin_users'))
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        user_entry = next((u for u in list_res.data if u['id'] == self.student_user.id), None)
        self.assertIsNotNone(user_entry)
        self.assertFalse(user_entry['is_active'])

    def test_c_admin_deactivates_instructor_and_persists(self):
        """TEST C: Admin deactivates Instructor, db is_active=False, refresh still shows inactive."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_user_detail', kwargs={'pk': self.instructor_user.id})

        res = self.client.patch(url, {'is_active': False}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['is_active'])

        self.instructor_user.refresh_from_db()
        self.assertFalse(self.instructor_user.is_active)

        # Refresh / list check
        list_res = self.client.get(reverse('admin_users'))
        user_entry = next((u for u in list_res.data if u['id'] == self.instructor_user.id), None)
        self.assertIsNotNone(user_entry)
        self.assertFalse(user_entry['is_active'])

    def test_d_and_e_admin_activates_inactive_user_and_persists(self):
        """TEST D & E: Admin activates inactive user, db is_active=True, refresh still shows active."""
        # Deactivate first
        self.student_user.is_active = False
        self.student_user.save(update_fields=['is_active'])

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_user_detail', kwargs={'pk': self.student_user.id})

        # TEST D: Activate user
        res = self.client.patch(url, {'is_active': True}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['is_active'])

        self.student_user.refresh_from_db()
        self.assertTrue(self.student_user.is_active)

        # TEST E: Fetch users again
        list_res = self.client.get(reverse('admin_users'))
        user_entry = next((u for u in list_res.data if u['id'] == self.student_user.id), None)
        self.assertIsNotNone(user_entry)
        self.assertTrue(user_entry['is_active'])

    def test_f_deactivated_user_cannot_login(self):
        """TEST F: Deactivated user cannot login."""
        self.student_user.is_active = False
        self.student_user.save(update_fields=['is_active'])

        self.client.force_authenticate(user=None)
        res = self.client.post(self.login_url, {
            'email': self.student_user.email,
            'password': 'Password@123'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('tokens', res.data)

    def test_g_activated_user_can_login(self):
        """TEST G: Activated user can login."""
        self.student_user.is_active = True
        self.student_user.save(update_fields=['is_active'])

        self.client.force_authenticate(user=None)
        res = self.client.post(self.login_url, {
            'email': self.student_user.email,
            'password': 'Password@123'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', res.data)

    def test_h_changing_role_does_not_reset_is_active(self):
        """TEST H: Changing role does NOT reset is_active."""
        # Start with an inactive instructor
        self.instructor_user.is_active = False
        self.instructor_user.save(update_fields=['is_active'])

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_user_detail', kwargs={'pk': self.instructor_user.id})

        # Change role to STUDENT
        res = self.client.patch(url, {'role': 'STUDENT'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['role'], 'STUDENT')
        self.assertFalse(res.data['is_active'])

        self.instructor_user.refresh_from_db()
        self.assertEqual(self.instructor_user.role, 'STUDENT')
        self.assertFalse(self.instructor_user.is_active)

    def test_i_admin_cannot_deactivate_own_active_admin_account(self):
        """TEST I: Admin cannot deactivate their own active admin account."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_user_detail', kwargs={'pk': self.admin_user.id})

        res = self.client.patch(url, {'is_active': False}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', res.data)

        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)
