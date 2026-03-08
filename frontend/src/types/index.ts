export type DiamondNodeLabel =
  | "Adversary"
  | "Infrastructure"
  | "Capability"
  | "Victim"
  | "Tag";

export interface DiamondNode {
  uid: string;
  workspace_id: string | null;
  label: DiamondNodeLabel;
  [key: string]: any;
}

export interface Adversary extends DiamondNode {
  name: string;
  aliases: string[];
  actor_type: string;
}

export interface Infrastructure extends DiamondNode {
  value: string;
  infra_type: string;
  provider: string | null;
}

export interface Capability extends DiamondNode {
  name: string;
  cap_type: string;
  version: string | null;
  hash: string | null;
}

export interface Victim extends DiamondNode {
  identity: string;
  sector: string | null;
  region: string | null;
}

export interface Relationship {
  relationship: {
    valid_from: number;
    valid_to: number | null;
    confidence: number;
    workspace_id: string | null;
    [key: string]: any;
  };
  target: DiamondNode;
  type: string;
}

export interface Conflict {
  uid: string;
  label: string;
  differences: Record<string, { production: any; workspace: any }>;
}
