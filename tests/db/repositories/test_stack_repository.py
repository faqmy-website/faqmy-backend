import pytest

from faqmy_backend.db.repositories.stack import StackRepository


@pytest.mark.parametrize(
    argnames="spec",
    argvalues=[
        {},
        {"name": "Stack Name"},
        {"description": "Description"},
        {"initial_question": "Initial question"},
        {"widget_delay": 5},
        {"color": "#336699"},
    ],
)
async def test_create_stack(user, stack_repo: StackRepository, spec):
    stack = await stack_repo.create(user.id, **spec)
    assert stack.id
    assert stack.user == user
    assert all(
        (getattr(stack, field) == value for field, value in spec.items())
    )


@pytest.mark.parametrize(
    argnames="spec",
    argvalues=[
        {},
        {"name": "New Stack Name"},
        {"description": "New Description"},
        {"initial_question": "New Initial Question"},
        {"widget_delay": 15},
        {"color": "#AABBCC"},
    ],
)
async def test_update_stack(user, stack_repo: StackRepository, spec):
    original_stack_data = {
        "name": "Original Stack Name",
        "description": "Original Description",
        "initial_question": "Original Initial Question",
        "widget_delay": 5,
        "color": "#336699",
    }

    stack = await stack_repo.create(user.id, **original_stack_data)
    await stack_repo.update(stack.id, **spec)

    stack = await stack_repo.get_by_id(stack.id)

    for field, value in original_stack_data.items():
        if field in spec:
            value = spec[field]
        assert getattr(stack, field) == value
