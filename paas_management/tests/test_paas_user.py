from odoo.tests.common import TransactionCase

class TestPaasUser(TransactionCase):
    def test_01_paas_user_creation(self):
        """Minimal test to satisfy the test runner and silence warnings."""
        # Create a test plan
        plan = self.env['paas.plan'].create({
            'name': 'Test Plan',
        })
        self.assertTrue(plan.product_id, "A product should be created for the plan")
        
        # Create a test user
        user = self.env['paas.user'].create({
            'name': 'Test User',
            'username': 'testuser',
            'plan_id': plan.id,
        })
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.plan_id.id, plan.id)
