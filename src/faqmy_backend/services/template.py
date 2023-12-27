from jinja2 import Environment, PackageLoader, Template, select_autoescape

env = Environment(
    loader=PackageLoader("faqmy_backend"),
    autoescape=select_autoescape(default=True),
)


__all__ = ["env", "Template"]
# confirmation_email_template = env.get_template("email/confirm_email.html")
# greeting_email_template = env.get_template("email/signup_greeting.html")
# forget_password_template = env.get_template("email/forget_password.html")
#
# html = forget_password_template.render(email="dfasdf<b><script></script>")
