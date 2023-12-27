from fastapi import APIRouter, Depends, status
from async_stripe import stripe

from faqmy_backend.app.dependencies import StackRepositoryDependMarker
from faqmy_backend.app.schemas import Widget
from faqmy_backend.db.models.conversations import MessageTypeEnum
from faqmy_backend.db.repositories.stack import StackRepository
from faqmy_backend.users.manager import fastapi_users
from faqmy_backend.conf import settings
from sqlalchemy import select
from faqmy_backend.db.models.users import User
from faqmy_backend.db.connection import create_session
from sqlalchemy import func
from faqmy_backend.db.models.conversations import (
    Conversation,
    Message
)
from faqmy_backend.db.models.stack import Stack


router = APIRouter()
current_user = fastapi_users.current_user()
stripe.api_key = settings.stripe.key
stripe.max_network_retries = 2
stripe.enable_telemetry = False

client = stripe.http_client.RequestsClient()
stripe.default_http_client = client


@router.get("/products", summary="Product List")
async def get_products():
    return await stripe.Product.list(active=True, limit=10)


async def get_customer(email):
    resp = await stripe.Customer.list(email=email, limit=1)
    customers = list(resp)
    if len(customers) == 0:
        return None
    customer_id = customers[0]['id']
    return customer_id


async def get_subscriptions(customer_id):
    resp = await stripe.Subscription.list(
        customer=customer_id,
        status='all',
        limit=10)
    return resp


@router.get("/subscription", summary="Subscription Details")
async def subscription_detail(
    user: User = Depends(current_user),
):
    # products = await get_products()
    customer_id = await get_customer(user.email)
    # customer does not exists
    if customer_id is None:
        return []

    subscriptions = await get_subscriptions(customer_id)

    filtered = []
    for subscription in list(subscriptions):
        if subscription['status'] in ['active', 'trialing']:
            filtered.append({'status': subscription['status'],
                             'id': subscription['id'],
                             'created': subscription['created'],
                             'start_date': subscription['start_date'],
                             'trial_start': subscription['trial_start'],
                             'trial_end': subscription['trial_end'],
                             'current_period_end': subscription['current_period_end'],
                             'current_period_start': subscription['current_period_start'],
                             'plan_id': subscription['plan']['id'],
                             'plan_interval': subscription['plan']['interval'],
                             'plan_interval_count': subscription['plan']['interval_count'],
                             'plan_amount': subscription['plan']['amount'],
                             'plan_product': subscription['plan']['product'],

                             # 'orig': subscription
                             })

    return filtered


@router.get("/constants", summary="Stripe constants")
async def get_stripe_constants():
    return {
        'customer_portal_url': settings.stripe.customer_portal_url,
        'pricing_table_id': settings.stripe.pricing_table_id,
        'publishable_key': settings.stripe.publishable_key,
    }


@router.get(
    "/widget/{id}",
    summary="Get widget status",
    status_code=status.HTTP_200_OK,
    response_model=Widget
)
async def widget_status(
    id: str,
    repo: StackRepository = Depends(StackRepositoryDependMarker),
):
    """
    Get the stack details
    \f
    :param id:
    :param repo:
    :return:
    """

    # get stack
    stack = await repo.get_by_id(id)
    if stack is None:
        return {'is_active': False,
                'reason': 'no stack found'}

    async with create_session() as session:
        user = (await session.execute(select(User).where(User.id == stack.user_id))).scalar()

        # get products
        products = list(await get_products())

        # get customer
        customer_id = await get_customer(user.email)
        # customer does not exists
        if customer_id is None:
            return {'is_active': False,
                    'reason': 'no customer found'}

        # get subscriptions
        subscriptions = list(await get_subscriptions(customer_id))
        filtered = []
        for subscription in subscriptions:
            if subscription['status'] in ['active', 'trialing']:
                filtered.append(subscription)
        if len(filtered) == 0:
            return {'is_active': False,
                    'reason': 'no active or trialing subscription found'}

        # count messages by period and compare with plan limit
        # if fits plan limit -> return good
        # if does not fit -> return bad

        # current subscription
        current_subcription = filtered[0]

        from datetime import datetime, timezone, timedelta
        import pytz

        tz = pytz.timezone('UTC')
        ts = current_subcription["current_period_start"]
        current_period_start = datetime.fromtimestamp(ts, tz)

        query = (
            select(func.count())
            .select_from(Message, Conversation, Stack)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .join(Stack, Stack.user_id == user.id)
            .filter(Conversation.stack_id == Stack.id)
            .filter(Message.who == MessageTypeEnum.user)
            .filter(Message.created_at > current_period_start)
        )
        actual_message_count = (await session.execute(query)).scalar_one()

        product_id = current_subcription['plan']['product']

        current_product = None
        for product in products:
            if product['id'] == product_id:
                current_product = product
                break

        if current_product is None:
            return {'is_active': False,
                    'reason': 'subscription product not found'}

        plan_message_count = int(current_product['metadata']['messages_count'])

        return {
            'is_active': True,
            'reason': 'all good',
            'metadata': {
                'actual_message_count': actual_message_count,
                'plan_message_count': plan_message_count,
                # 'current_subcription': current_subcription,
                # 'products': products
            }
        }

    return {
        'is_active': False,
        'reason': 'not sure for what reason'
    }
