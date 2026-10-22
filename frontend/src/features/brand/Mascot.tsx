import type { CSSProperties, ReactElement } from "react";

/**
 * Original NeuroQuest characters: three soft "neurons" that stand for the
 * three sectors (cloud = AI, squircle = cyber safety, bean = money).
 * Purely decorative, hence aria-hidden.
 */
export type MascotKind = "cloud" | "squircle" | "bean";

const BODY: Record<MascotKind, { fill: string; shape: ReactElement; face: [number, number] }> = {
  cloud: {
    fill: "var(--lilac)",
    face: [60, 66],
    shape: (
      <path d="M32 94C15 94 5 82 5 68c0-13 9-22 21-24C29 24 44 12 62 12c16 0 29 9 34 23 16 1 28 12 28 28 0 17-13 31-30 31z" />
    ),
  },
  squircle: {
    fill: "var(--cobalt)",
    face: [60, 62],
    shape: <rect x="12" y="12" width="96" height="96" rx="36" transform="rotate(-7 60 60)" />,
  },
  bean: {
    fill: "var(--coral)",
    face: [58, 64],
    shape: (
      <path d="M36 10c24-8 50 5 55 33 5 26-4 53-28 63-22 9-47-3-51-29C7 51 13 18 36 10z" />
    ),
  },
};

export function Mascot({
  kind,
  size = 120,
  className = "",
  style,
}: {
  kind: MascotKind;
  size?: number;
  className?: string;
  style?: CSSProperties;
}) {
  const { fill, shape, face } = BODY[kind];
  const [fx, fy] = face;
  return (
    <svg
      className={`mascot ${className}`}
      style={style}
      width={size}
      height={size}
      viewBox="0 0 120 120"
      aria-hidden="true"
      focusable="false"
    >
      <g fill={fill}>{shape}</g>
      {/* shine */}
      <ellipse cx={fx - 20} cy={fy - 26} rx="9" ry="5" fill="#fff" opacity=".35" transform={`rotate(-30 ${fx - 20} ${fy - 26})`} />
      {/* face */}
      <ellipse cx={fx - 15} cy={fy - 4} rx="5.2" ry="6.6" fill="var(--ink)" />
      <ellipse cx={fx + 15} cy={fy - 4} rx="5.2" ry="6.6" fill="var(--ink)" />
      <circle cx={fx - 13.4} cy={fy - 6.4} r="1.7" fill="#fff" />
      <circle cx={fx + 16.6} cy={fy - 6.4} r="1.7" fill="#fff" />
      <circle cx={fx - 27} cy={fy + 8} r="5" fill="var(--coral)" opacity=".45" />
      <circle cx={fx + 27} cy={fy + 8} r="5" fill="var(--coral)" opacity=".45" />
      <path d={`M${fx - 8} ${fy + 8}q8 8 16 0`} fill="none" stroke="var(--ink)" strokeWidth="3.4" strokeLinecap="round" />
    </svg>
  );
}

/** four-point sparkle, the page's only ornament */
export function Sparkle({ size = 28, color = "var(--butter)", className = "" }: { size?: number; color?: string; className?: string }) {
  return (
    <svg className={`sparkle ${className}`} width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path fill={color} d="M12 0c1.2 6.6 3.4 10.8 12 12-8.6 1.2-10.8 5.4-12 12-1.2-6.6-3.4-10.8-12-12C8.6 10.8 10.8 6.6 12 0z" />
    </svg>
  );
}
