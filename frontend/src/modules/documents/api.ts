import client from "../../api/client";
import type { Document, DocumentCreate } from "../../types";

export const documentsApi = {
  getAll: () => client.get<Document[]>("/documents").then((res) => res.data),

  create: (data: DocumentCreate) =>
    client.post<Document>("/documents", data).then((res) => res.data),
};
