"use client";

import { useLayoutEffect, useRef } from "react";

/** A ref that always holds the latest value, for use inside animation loops and timers. */
export function useLatest<T>(value: T) {
  const ref = useRef(value);
  useLayoutEffect(() => {
    ref.current = value;
  });
  return ref;
}
