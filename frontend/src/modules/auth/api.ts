import client from "../../api/client";
import type { LoginRequest, RegisterRequest, Token, User } from "../../types";

export const authApi = {
  login: (data: LoginRequest) =>
    client.post<Token>("/auth/login", data).then((res) => res.data),

  register: (data: RegisterRequest) =>
    client.post<User>("/auth/register", data).then((res) => res.data),
};
