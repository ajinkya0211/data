from fastapi import APIRouter

from app.api.v1.endpoints import projects, datasets, auth, ai_agent, blocks, websocket, workflows, mcp_ai_agent

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(blocks.router, prefix="/blocks", tags=["blocks"])
api_router.include_router(ai_agent.router, prefix="/ai", tags=["ai-agent"])
api_router.include_router(websocket.router, prefix="", tags=["websocket"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(mcp_ai_agent.router, prefix="/mcp-ai", tags=["mcp-ai-agent"]) 