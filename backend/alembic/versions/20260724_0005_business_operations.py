"""Add business operations records.

Revision ID: 20260724_0005
Revises: 20260723_0004
"""
import sqlalchemy as sa
from alembic import op
revision="20260724_0005"; down_revision="20260723_0004"; branch_labels=None; depends_on=None
def audit(): return [sa.Column("created_at",sa.DateTime(),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False),sa.Column("updated_at",sa.DateTime(),server_default=sa.text("CURRENT_TIMESTAMP"),nullable=False)]
def upgrade():
 op.create_table("employees",sa.Column("id",sa.String(36),primary_key=True),sa.Column("startup_profile_id",sa.String(36),nullable=False),sa.Column("full_name",sa.String(160),nullable=False),sa.Column("job_title",sa.String(120)),sa.Column("employment_status",sa.String(24),nullable=False),*audit(),sa.ForeignKeyConstraint(["startup_profile_id"],["startup_profiles.id"],ondelete="CASCADE"));op.create_index("ix_employees_profile_status","employees",["startup_profile_id","employment_status"])
 op.create_table("attendance_records",sa.Column("id",sa.String(36),primary_key=True),sa.Column("employee_id",sa.String(36),nullable=False),sa.Column("attendance_date",sa.Date(),nullable=False),sa.Column("status",sa.String(24),nullable=False),*audit(),sa.ForeignKeyConstraint(["employee_id"],["employees.id"],ondelete="CASCADE"),sa.UniqueConstraint("employee_id","attendance_date",name="uq_attendance_employee_date"))
 op.create_table("leave_requests",sa.Column("id",sa.String(36),primary_key=True),sa.Column("employee_id",sa.String(36),nullable=False),sa.Column("start_date",sa.Date(),nullable=False),sa.Column("end_date",sa.Date(),nullable=False),sa.Column("reason",sa.Text()),sa.Column("status",sa.String(24),nullable=False),*audit(),sa.ForeignKeyConstraint(["employee_id"],["employees.id"],ondelete="CASCADE"))
 op.create_table("operation_tasks",sa.Column("id",sa.String(36),primary_key=True),sa.Column("startup_profile_id",sa.String(36),nullable=False),sa.Column("title",sa.String(240),nullable=False),sa.Column("assigned_employee_id",sa.String(36)),sa.Column("status",sa.String(24),nullable=False),*audit(),sa.ForeignKeyConstraint(["startup_profile_id"],["startup_profiles.id"],ondelete="CASCADE"),sa.ForeignKeyConstraint(["assigned_employee_id"],["employees.id"],ondelete="SET NULL"));op.create_index("ix_operation_tasks_profile_status","operation_tasks",["startup_profile_id","status"])
 op.create_table("announcements",sa.Column("id",sa.String(36),primary_key=True),sa.Column("startup_profile_id",sa.String(36),nullable=False),sa.Column("message",sa.Text(),nullable=False),*audit(),sa.ForeignKeyConstraint(["startup_profile_id"],["startup_profiles.id"],ondelete="CASCADE"))
def downgrade():
 op.drop_table("announcements");op.drop_table("operation_tasks");op.drop_table("leave_requests");op.drop_table("attendance_records");op.drop_table("employees")
