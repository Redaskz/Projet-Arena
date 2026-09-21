import { get } from "./client";
import type { Tournament } from "../types";

export function getTournaments(): Promise<Tournament[]> {
  return get<Tournament[]>("/tournaments");
}