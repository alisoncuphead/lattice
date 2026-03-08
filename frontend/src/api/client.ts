import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
});

export const setWorkspaceHeader = (workspaceId: string | null) => {
  if (workspaceId) {
    client.defaults.headers.common["X-Lattice-Workspace"] = workspaceId;
  } else {
    delete client.defaults.headers.common["X-Lattice-Workspace"];
  }
};

export default client;
