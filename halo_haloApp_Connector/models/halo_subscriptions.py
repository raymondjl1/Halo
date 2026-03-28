from odoo import models, fields, api
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import json
from datetime import datetime, timedelta

class HaloSubscriptions(models.Model):
    _name = 'halo.cus.subscriptions'
    _description = 'Halo Subscriptions'

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    order_id = fields.Many2one('sale.order', string='Sales Order', required=True)
    user_group_id = fields.Many2one('halo.cus.application.user.groups', string='User Group', required=True)
    expiration_date = fields.Datetime(string='Expiration Date')
    key_value = fields.Text(string='License Key')

    @api.model
    def generate_key_from_passphrase(self, passphrase: str, salt: bytes):
        """
        Generates a cryptographic key from a passphrase and salt using PBKDF2.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Length of the key (32 bytes = 256 bits for Fernet)
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    @api.model
    def halo_build_key(self, customer_id, sales_order_id, expiration_days, user_group_id, send_email=True):
        passphrase = "HaloProtects01!"  # Hardcoded passphrase
        salt = b"fixed_salt_value"  # Hardcoded salt (you can store it securely and make sure it is unique)

        # Generate the derived key from the passphrase and salt
        derived_key = self.generate_key_from_passphrase(passphrase, salt)

        # Initialize Fernet with the derived key
        fernet = Fernet(derived_key)
        
        # Set the expiration date
        expiration_date = datetime.now() + timedelta(days=expiration_days)
        
        # Prepare the data to be encrypted
        key_data = {
            'customer_id': customer_id,
            'order_id': sales_order_id,
            'user_group_name': user_group_id.name,
            'expiration_date': expiration_date.isoformat()
        }
        
        # Encrypt the data
        encrypted_data = fernet.encrypt(json.dumps(key_data).encode())
        
        # Prepare the subscription values
        subscription_vals = {
            'customer_id': customer_id,
            'order_id': sales_order_id,
            'user_group_name': user_group_id.name,
            'expiration_date': expiration_date,
            'key_value': base64.b64encode(encrypted_data).decode()
        }
        
       
        
        # Send email to the customer if specified
        if send_email:
            # Create the subscription record
            subscription = self.create(subscription_vals)
            template = self.env.ref('halo_app.email_template_subscription_key')
            template.send_mail(subscription.id, force_send=True)
        
            return subscription
        else:
            return subscription_vals

    def action_regenerate_key(self):
        # Regenerate key by calling halo_build_key
        for record in self:
            # Define the expiration days as needed, you can adjust this value
            expiration_days = 365  # Example: 1 year for key expiration
            subscription_vals = self.halo_build_key(
                record.customer_id.id, 
                record.order_id.id, 
                expiration_days, 
                record.user_group_id,
                send_email=False
            )
            # Update the current record with the new key
            record.key_value = subscription_vals['key_value']
            record.expiration_date = subscription_vals['expiration_date']
        return True
