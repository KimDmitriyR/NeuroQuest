"""link quest start node fk

Revision ID: 3e1919a18504
Revises: ab0c936f17c9
Create Date: 2026-09-23 16:21:32.597302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e1919a18504'
down_revision: Union[str, Sequence[str], None] = 'ab0c936f17c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        "fk_quests_start_node_id_quest_nodes",
        "quests",
        "quest_nodes",
        ["start_node_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_quests_start_node_id_quest_nodes", "quests", type_="foreignkey"
    )
