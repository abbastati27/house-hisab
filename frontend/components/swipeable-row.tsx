"use client";

import { useRef, useState } from "react";

export function SwipeableRow({ children, rightActions, className = "" }:{ children: React.ReactNode; rightActions: React.ReactNode; className?: string }){
  const startX = useRef<number | null>(null);
  const currentX = useRef<number>(0);
  const [offset, setOffset] = useState(0);
  const [open, setOpen] = useState(false);

  function onTouchStart(e: React.TouchEvent){
    startX.current = e.touches[0].clientX;
    currentX.current = offset;
  }
  function onTouchMove(e: React.TouchEvent){
    if (startX.current == null) return;
    const dx = e.touches[0].clientX - startX.current;
    let next = currentX.current + dx;
    // constrain to left swipe only, max -160px
    next = Math.min(0, Math.max(-160, next));
    setOffset(next);
  }
  function onTouchEnd(){
    // snap
    const shouldOpen = offset < -72; // threshold
    setOpen(shouldOpen);
    setOffset(shouldOpen ? -128 : 0);
    startX.current = null;
  }
  function close(){ setOpen(false); setOffset(0); }

  return (
    <div className={`relative overflow-hidden select-none ${className}`}>
      <div className="absolute inset-y-0 right-0 flex items-stretch gap-1 pr-2 pl-4" aria-hidden>
        {rightActions}
      </div>
      <div
        className="bg-white"
        style={{ transform: `translateX(${offset}px)`, transition: startX.current==null ? "transform 160ms ease" : "none" }}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
        onTouchCancel={onTouchEnd}
        onClick={close}
      >
        {children}
      </div>
    </div>
  );
}
