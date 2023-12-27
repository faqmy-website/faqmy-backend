from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from aiosmtplib import SMTP

from faqmy_backend.conf import settings
from faqmy_backend.services.template import Template, env


class EmailSender:
    def __init__(self):
        self.smtp_client = SMTP(
            hostname=settings.smtp.server,
            port=settings.smtp.port,
            username=settings.smtp.login,
            password=settings.smtp.key,
        )

    async def send_mail(
        self,
        to: str | list[str],
        subject: str,
        text: str | None = None,
        html: str | None = None,
        from_email: str | None = None,
    ):
        message = await self.compose_message(
            to=to,
            subject=subject,
            from_email=from_email,
            text=text,
            html=html,
        )
        async with self.smtp_client as c:
            await c.send_message(message)

    async def compose_message(
        self,
        to: str | list[str],
        subject: str,
        text: str | None = None,
        html: str | None = None,
        from_email: str | None = None,
    ) -> EmailMessage:
        """"""
        if html:
            message = MIMEMultipart()
            message.attach(MIMEText(html, "html"))
            if text:
                message.attach(MIMEText(text, "plain"))
        else:
            message = EmailMessage()
            if text:
                message.set_content(text)

        message["From"] = from_email or settings.smtp.default_from_email
        message["To"] = to
        message["Subject"] = subject

        return message


class EmailNotification:
    subject: str
    template_name: str
    template_obj: Template
    from_email: str

    @classmethod
    async def send(cls, to: str, context: dict[str, Any] | None = None):
        await EmailSender().send_mail(
            to=to,
            subject=await cls.render_subject(context),
            html=await cls.render_body(context),
        )

    @classmethod
    async def render_subject(
        cls, context: dict[str, Any] | None = None
    ) -> str:
        return cls.subject

    @classmethod
    async def render_body(cls, context: dict[str, Any] | None = None) -> str:
        if not hasattr(cls, "template_obj"):
            cls.template_obj = env.get_template(cls.template_name)
        return cls.template_obj.render(**(context or {}))


class ForgetPasswordEmailNotification(EmailNotification):
    subject: str = "Password recovery on faqmy.website"
    template_name: str = "email/forget_password.html"


class ConfirmEmailNotification(EmailNotification):
    subject: str = "Confirm your email on faqmy.website"
    template_name: str = "email/confirm_email.html"


class SignupGreetingEmailNotification(EmailNotification):
    subject: str = "Welcome to faqmy.website"
    template_name: str = "email/signup_greeting.html"


class EmailConfirmationDoneEmailNotification(EmailNotification):
    subject: str = "Your faqmy.website account email confirmed successfully"
    template_name: str = "email/email_confirmation_done.html"
