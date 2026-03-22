from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `interview_session` ADD `expression_records` JSON NOT NULL  COMMENT '表情记录列表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `interview_session` DROP COLUMN `expression_records`;"""
