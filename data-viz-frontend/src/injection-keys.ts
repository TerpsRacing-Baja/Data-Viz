import { InjectionKey } from "vue";
import type { Emitter } from "mitt";

// This specifies the types of events we emit, note the optional flag b/c there could be one of several type
type Events = {
  "car-state"?: { lat: number; lon: number };
};

// Contains both a unique symbol and
export const EMITTER_KEY: InjectionKey<Emitter<Events>> = Symbol("emitter");
