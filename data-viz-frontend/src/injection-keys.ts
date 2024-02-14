import { InjectionKey } from "vue";
import type { Emitter } from "mitt";
import type { Events } from "./emitter-messages";

// Contains both a unique symbol and type associated message types
export const EMITTER_KEY: InjectionKey<Emitter<Events>> = Symbol("emitter");
