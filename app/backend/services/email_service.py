"""
Email Service for Titelli
Handles transactional emails: referral notifications, payment confirmations, etc.
Uses Resend API for reliable email delivery.
"""
import os
import asyncio
import logging
import resend
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

logger = logging.getLogger(__name__)

# Configure Resend
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
TITELLI_LOGO = "https://image-fix-demo.preview.emergentagent.com/logo192.png"


# ============ EMAIL TEMPLATES ============

def get_referral_success_template(referrer_name: str, referee_name: str, points_earned: int, total_referrals: int) -> str:
    """Template for notifying referrer when someone uses their code"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #18181b;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #18181b; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #27272a; border-radius: 16px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); padding: 30px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">🎉 Nouveau Parrainage !</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px;">
                                <p style="color: #ffffff; font-size: 18px; margin-bottom: 20px;">
                                    Bonjour <strong>{referrer_name}</strong> !
                                </p>
                                
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    Excellente nouvelle ! <strong style="color: #a855f7;">{referee_name}</strong> vient de s'inscrire sur Titelli avec votre code de parrainage.
                                </p>
                                
                                <!-- Points Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td style="background-color: #3f3f46; border-radius: 12px; padding: 20px; text-align: center;">
                                            <p style="color: #a855f7; font-size: 36px; font-weight: bold; margin: 0;">+{points_earned}</p>
                                            <p style="color: #a1a1aa; font-size: 14px; margin: 5px 0 0 0;">points gagnés</p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #a1a1aa; font-size: 14px; line-height: 1.6;">
                                    📊 Vous avez maintenant parrainé <strong style="color: white;">{total_referrals} personne(s)</strong> au total.
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td align="center">
                                            <a href="https://image-fix-demo.preview.emergentagent.com/dashboard/client?tab=parrainage" 
                                               style="display: inline-block; background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                                                Voir mes parrainages
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #71717a; font-size: 13px; margin-top: 20px;">
                                    Continuez à partager votre code pour gagner encore plus de points et débloquer des bonus !
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #18181b; padding: 20px; text-align: center; border-top: 1px solid #3f3f46;">
                                <p style="color: #71717a; font-size: 12px; margin: 0;">
                                    © 2026 Titelli - Social Commerce Suisse<br>
                                    <a href="https://image-fix-demo.preview.emergentagent.com" style="color: #a855f7; text-decoration: none;">titelli.ch</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def get_welcome_bonus_template(user_name: str, referrer_name: str, bonus_points: int) -> str:
    """Template for welcoming new user with referral bonus"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #18181b;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #18181b; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #27272a; border-radius: 16px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #d4af37 0%, #f5d67b 100%); padding: 30px; text-align: center;">
                                <h1 style="color: #18181b; margin: 0; font-size: 24px;">✨ Bienvenue sur Titelli !</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px;">
                                <p style="color: #ffffff; font-size: 18px; margin-bottom: 20px;">
                                    Bonjour <strong>{user_name}</strong> !
                                </p>
                                
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    Bienvenue dans la communauté Titelli ! Grâce à <strong style="color: #d4af37;">{referrer_name}</strong>, vous commencez avec un bonus spécial.
                                </p>
                                
                                <!-- Bonus Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td style="background-color: #3f3f46; border-radius: 12px; padding: 20px; text-align: center;">
                                            <p style="color: #d4af37; font-size: 36px; font-weight: bold; margin: 0;">+{bonus_points}</p>
                                            <p style="color: #a1a1aa; font-size: 14px; margin: 5px 0 0 0;">points de bienvenue</p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #a1a1aa; font-size: 14px; line-height: 1.6;">
                                    🎁 Ces points sont déjà crédités sur votre compte. Utilisez-les pour débloquer des avantages exclusifs !
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td align="center">
                                            <a href="https://image-fix-demo.preview.emergentagent.com/dashboard/client" 
                                               style="display: inline-block; background: linear-gradient(135deg, #d4af37 0%, #f5d67b 100%); color: #18181b; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                                                Découvrir Titelli
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Features -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 20px 0;">
                                    <tr>
                                        <td style="color: #a1a1aa; font-size: 14px; padding: 10px 0;">
                                            💕 <strong style="color: white;">RDV chez Titelli</strong> - Partagez des activités à deux
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="color: #a1a1aa; font-size: 14px; padding: 10px 0;">
                                            ⚽ <strong style="color: white;">Sports</strong> - Trouvez des partenaires sportifs
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="color: #a1a1aa; font-size: 14px; padding: 10px 0;">
                                            🎁 <strong style="color: white;">Parrainage</strong> - Gagnez +50 pts par ami invité
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #18181b; padding: 20px; text-align: center; border-top: 1px solid #3f3f46;">
                                <p style="color: #71717a; font-size: 12px; margin: 0;">
                                    © 2026 Titelli - Social Commerce Suisse<br>
                                    <a href="https://image-fix-demo.preview.emergentagent.com" style="color: #d4af37; text-decoration: none;">titelli.ch</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def get_referral_bonus_template(user_name: str, milestone: int, bonus_points: int, total_referrals: int) -> str:
    """Template for bonus milestone notification"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #18181b;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #18181b; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #27272a; border-radius: 16px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%); padding: 30px; text-align: center;">
                                <h1 style="color: #18181b; margin: 0; font-size: 24px;">🏆 Bonus Débloqué !</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px;">
                                <p style="color: #ffffff; font-size: 18px; margin-bottom: 20px;">
                                    Félicitations <strong>{user_name}</strong> !
                                </p>
                                
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    Vous avez atteint le palier de <strong style="color: #fbbf24;">{milestone} parrainages</strong> ! Un bonus spécial a été crédité sur votre compte.
                                </p>
                                
                                <!-- Bonus Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td style="background-color: #3f3f46; border-radius: 12px; padding: 20px; text-align: center;">
                                            <p style="color: #fbbf24; font-size: 48px; font-weight: bold; margin: 0;">+{bonus_points}</p>
                                            <p style="color: #a1a1aa; font-size: 14px; margin: 5px 0 0 0;">points bonus</p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #a1a1aa; font-size: 14px; line-height: 1.6;">
                                    📊 Total parrainages : <strong style="color: white;">{total_referrals}</strong>
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td align="center">
                                            <a href="https://image-fix-demo.preview.emergentagent.com/dashboard/client?tab=parrainage" 
                                               style="display: inline-block; background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%); color: #18181b; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                                                Voir mes récompenses
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #18181b; padding: 20px; text-align: center; border-top: 1px solid #3f3f46;">
                                <p style="color: #71717a; font-size: 12px; margin: 0;">
                                    © 2026 Titelli - Social Commerce Suisse<br>
                                    <a href="https://image-fix-demo.preview.emergentagent.com" style="color: #fbbf24; text-decoration: none;">titelli.ch</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# ============ EMAIL SENDING FUNCTIONS ============

async def send_email(to_email: str, subject: str, html_content: str) -> dict:
    """Send an email using Resend API (non-blocking)"""
    if not resend.api_key:
        logger.warning("RESEND_API_KEY not configured, skipping email")
        return {"status": "skipped", "reason": "No API key"}
    
    params = {
        "from": f"Titelli <{SENDER_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {subject}")
        return {"status": "success", "email_id": email.get("id")}
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return {"status": "error", "error": str(e)}


async def send_referral_notification(
    referrer_email: str,
    referrer_name: str,
    referee_name: str,
    points_earned: int,
    total_referrals: int
) -> dict:
    """Send notification to referrer when someone uses their code"""
    html = get_referral_success_template(referrer_name, referee_name, points_earned, total_referrals)
    return await send_email(
        to_email=referrer_email,
        subject=f"🎉 {referee_name} a utilisé votre code ! +{points_earned} points",
        html_content=html
    )


async def send_welcome_bonus_notification(
    user_email: str,
    user_name: str,
    referrer_name: str,
    bonus_points: int
) -> dict:
    """Send welcome email to new user with referral bonus"""
    html = get_welcome_bonus_template(user_name, referrer_name, bonus_points)
    return await send_email(
        to_email=user_email,
        subject=f"✨ Bienvenue sur Titelli ! +{bonus_points} points bonus",
        html_content=html
    )


async def send_bonus_milestone_notification(
    user_email: str,
    user_name: str,
    milestone: int,
    bonus_points: int,
    total_referrals: int
) -> dict:
    """Send notification when user reaches a referral milestone"""
    html = get_referral_bonus_template(user_name, milestone, bonus_points, total_referrals)
    return await send_email(
        to_email=user_email,
        subject=f"🏆 Bonus {milestone} parrainages débloqué ! +{bonus_points} points",
        html_content=html
    )


# ============ PAYMENT CONFIRMATION TEMPLATES ============

def get_payment_confirmation_template(
    user_name: str,
    service_name: str,
    amount: float,
    currency: str = "CHF",
    subscription_type: str = None,
    next_billing_date: str = None
) -> str:
    """Template for payment/subscription confirmation"""
    is_subscription = subscription_type is not None
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #18181b;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #18181b; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #27272a; border-radius: 16px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #10b981 0%, #34d399 100%); padding: 30px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">✅ Paiement Confirmé</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px;">
                                <p style="color: #ffffff; font-size: 18px; margin-bottom: 20px;">
                                    Bonjour <strong>{user_name}</strong>,
                                </p>
                                
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    Votre {'abonnement' if is_subscription else 'paiement'} a été traité avec succès !
                                </p>
                                
                                <!-- Receipt Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0; background-color: #3f3f46; border-radius: 12px;">
                                    <tr>
                                        <td style="padding: 20px;">
                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="color: #a1a1aa; font-size: 14px; padding: 8px 0;">Service</td>
                                                    <td style="color: #ffffff; font-size: 14px; padding: 8px 0; text-align: right; font-weight: bold;">{service_name}</td>
                                                </tr>
                                                <tr>
                                                    <td style="color: #a1a1aa; font-size: 14px; padding: 8px 0;">Montant</td>
                                                    <td style="color: #10b981; font-size: 18px; padding: 8px 0; text-align: right; font-weight: bold;">{amount:.2f} {currency}</td>
                                                </tr>
                                                {'<tr><td style="color: #a1a1aa; font-size: 14px; padding: 8px 0;">Type</td><td style="color: #ffffff; font-size: 14px; padding: 8px 0; text-align: right;">' + subscription_type + '</td></tr>' if is_subscription else ''}
                                                {'<tr><td style="color: #a1a1aa; font-size: 14px; padding: 8px 0;">Prochain prélèvement</td><td style="color: #ffffff; font-size: 14px; padding: 8px 0; text-align: right;">' + next_billing_date + '</td></tr>' if next_billing_date else ''}
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #71717a; font-size: 13px; margin-top: 20px;">
                                    {'Votre abonnement sera automatiquement renouvelé. Vous pouvez le gérer depuis votre tableau de bord.' if is_subscription else 'Merci pour votre confiance !'}
                                </p>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td align="center">
                                            <a href="https://image-fix-demo.preview.emergentagent.com/dashboard/client" 
                                               style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #34d399 100%); color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                                                Voir mon compte
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #18181b; padding: 20px; text-align: center; border-top: 1px solid #3f3f46;">
                                <p style="color: #71717a; font-size: 12px; margin: 0;">
                                    © 2026 Titelli - Social Commerce Suisse<br>
                                    <a href="https://image-fix-demo.preview.emergentagent.com" style="color: #10b981; text-decoration: none;">titelli.ch</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


async def send_payment_confirmation(
    user_email: str,
    user_name: str,
    service_name: str,
    amount: float,
    currency: str = "CHF",
    subscription_type: str = None,
    next_billing_date: str = None
) -> dict:
    """Send payment/subscription confirmation email"""
    html = get_payment_confirmation_template(
        user_name, service_name, amount, currency, subscription_type, next_billing_date
    )
    
    subject = f"✅ {'Abonnement' if subscription_type else 'Paiement'} confirmé - {service_name}"
    
    return await send_email(
        to_email=user_email,
        subject=subject,
        html_content=html
    )



def get_payment_failed_template(user_name: str, service_name: str) -> str:
    """Template for payment failure notification"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #18181b;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #18181b; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #27272a; border-radius: 16px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #ef4444 0%, #f87171 100%); padding: 30px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">⚠️ Paiement non effectué</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px;">
                                <p style="color: #ffffff; font-size: 18px; margin-bottom: 20px;">
                                    Bonjour <strong>{user_name}</strong>,
                                </p>
                                
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    Nous n'avons pas pu traiter votre paiement pour <strong style="color: #f87171;">{service_name}</strong>.
                                </p>
                                
                                <p style="color: #a1a1aa; font-size: 14px; line-height: 1.6; margin-top: 20px;">
                                    Cela peut arriver pour plusieurs raisons :
                                </p>
                                
                                <ul style="color: #a1a1aa; font-size: 14px; line-height: 1.8;">
                                    <li>Fonds insuffisants</li>
                                    <li>Carte expirée ou bloquée</li>
                                    <li>Limite de transaction atteinte</li>
                                    <li>Problème technique temporaire</li>
                                </ul>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td align="center">
                                            <a href="https://image-fix-demo.preview.emergentagent.com/dashboard/client" 
                                               style="display: inline-block; background: linear-gradient(135deg, #0047AB 0%, #D4AF37 100%); color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                                                Réessayer le paiement
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #71717a; font-size: 13px; margin-top: 20px;">
                                    Si vous avez des questions, contactez notre support à support@titelli.ch
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #18181b; padding: 20px; text-align: center; border-top: 1px solid #3f3f46;">
                                <p style="color: #71717a; font-size: 12px; margin: 0;">
                                    © 2026 Titelli - Social Commerce Suisse<br>
                                    <a href="https://image-fix-demo.preview.emergentagent.com" style="color: #d4af37; text-decoration: none;">titelli.ch</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


async def send_payment_failed(
    user_email: str,
    user_name: str,
    service_name: str
) -> dict:
    """Send payment failure notification email"""
    html = get_payment_failed_template(user_name, service_name)
    
    return await send_email(
        to_email=user_email,
        subject=f"⚠️ Paiement non effectué - {service_name}",
        html_content=html
    )


# ============ PUB MÉDIA CONFIRMATION ============

def get_pub_media_confirmation_template(
    user_name: str,
    order_id: str,
    template_name: str,
    amount: float,
    slogan: str,
    product_name: str
) -> str:
    """Template for Pub Média order confirmation after payment"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #18181b;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #18181b; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #27272a; border-radius: 16px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); padding: 30px; text-align: center;">
                                <h1 style="color: white; margin: 0; font-size: 24px;">🎨 Commande Pub Média Confirmée !</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px;">
                                <p style="color: #ffffff; font-size: 18px; margin-bottom: 20px;">
                                    Bonjour <strong>{user_name}</strong>,
                                </p>
                                
                                <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    Merci pour votre commande ! Votre publicité personnalisée est en cours de création.
                                </p>
                                
                                <!-- Order Details Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0; background-color: #3f3f46; border-radius: 12px;">
                                    <tr>
                                        <td style="padding: 20px;">
                                            <p style="color: #f59e0b; font-size: 12px; text-transform: uppercase; margin: 0 0 15px 0; letter-spacing: 1px;">
                                                Détails de la commande
                                            </p>
                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="color: #a1a1aa; font-size: 14px; padding: 8px 0;">N° Commande</td>
                                                    <td style="color: #ffffff; font-size: 14px; padding: 8px 0; text-align: right; font-weight: bold;">#{order_id}</td>
                                                </tr>
                                                <tr>
                                                    <td style="color: #a1a1aa; font-size: 14px; padding: 8px 0;">Template</td>
                                                    <td style="color: #ffffff; font-size: 14px; padding: 8px 0; text-align: right;">{template_name}</td>
                                                </tr>
                                                <tr>
                                                    <td style="color: #a1a1aa; font-size: 14px; padding: 8px 0;">Produit</td>
                                                    <td style="color: #ffffff; font-size: 14px; padding: 8px 0; text-align: right;">{product_name}</td>
                                                </tr>
                                                <tr>
                                                    <td style="color: #a1a1aa; font-size: 14px; padding: 8px 0;">Slogan</td>
                                                    <td style="color: #f59e0b; font-size: 14px; padding: 8px 0; text-align: right; font-style: italic;">"{slogan}"</td>
                                                </tr>
                                                <tr style="border-top: 1px solid #52525b;">
                                                    <td style="color: #a1a1aa; font-size: 14px; padding: 12px 0 0 0;">Montant payé</td>
                                                    <td style="color: #10b981; font-size: 18px; padding: 12px 0 0 0; text-align: right; font-weight: bold;">{amount:.2f} CHF</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Status Info -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 20px 0; background-color: #1e3a2f; border: 1px solid #10b981; border-radius: 8px;">
                                    <tr>
                                        <td style="padding: 15px;">
                                            <p style="color: #10b981; font-size: 14px; margin: 0;">
                                                ✅ <strong>Image HD sans filigrane</strong> disponible après génération (~2-5 minutes)
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 25px 0;">
                                    <tr>
                                        <td align="center">
                                            <a href="https://image-fix-demo.preview.emergentagent.com/dashboard/entreprise?tab=commandes-titelli" 
                                               style="display: inline-block; background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                                                📥 Voir mes commandes
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="color: #71717a; font-size: 13px; margin-top: 20px; text-align: center;">
                                    Une notification vous sera envoyée dès que votre publicité sera prête à télécharger.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #18181b; padding: 20px; text-align: center; border-top: 1px solid #3f3f46;">
                                <p style="color: #71717a; font-size: 12px; margin: 0;">
                                    © 2026 Titelli - Pub Média IA<br>
                                    <a href="https://image-fix-demo.preview.emergentagent.com/media-pub" style="color: #f59e0b; text-decoration: none;">Créer une autre publicité</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


async def send_pub_media_confirmation(
    user_email: str,
    user_name: str,
    order_id: str,
    template_name: str,
    amount: float,
    slogan: str,
    product_name: str
) -> dict:
    """Send Pub Média order confirmation email after payment"""
    html = get_pub_media_confirmation_template(
        user_name=user_name,
        order_id=order_id,
        template_name=template_name,
        amount=amount,
        slogan=slogan,
        product_name=product_name
    )
    
    return await send_email(
        to_email=user_email,
        subject=f"🎨 Commande Pub Média #{order_id} confirmée - Titelli",
        html_content=html
    )
