import { request } from "./client";

export const sendChatMessage = ({ message, conversationId, projectId }) =>
  request({
    url: "/assistant/chat",
    method: "POST",
    data: { message, conversation_id: conversationId, project_id: projectId },
  });

export const getSuggestions = () => request({ url: "/assistant/suggestions" });
