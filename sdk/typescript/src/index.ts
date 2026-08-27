/**
 * Official TypeScript Client SDK for NhanThuat Platform.
 * Supports Node.js, Next.js, and browser environments.
 */

export interface NhanThuatClientConfig {
  baseUrl?: string;
  apiKey?: string;
  timeoutMs?: number;
}

export interface KnowledgeUnitCitation {
  id: string;
  title: string;
  domain: string;
}

export interface ActionScript {
  position_analysis: string;
  step_1_anchor?: { title: string; verbatim: string };
  step_2_deadline_consequence?: { title: string; verbatim: string };
  step_3_way_out_plan_b?: { title: string; verbatim: string };
  draft_official_communication?: string;
  financial_and_operational_directives?: string[];
  [key: string]: any;
}

export interface AnalysisResponse {
  status: "success" | "error";
  scenario_type: string;
  is_ambiguous: boolean;
  ambiguity_warning: string | null;
  philosophy_routing: {
    primary_philosophy: string;
    secondary_philosophies: string[];
    confidence_score: number;
    rationale: string;
  };
  matched_knowledge_units: Array<{
    id: string;
    title: string;
    domain: string;
    type: string;
    summary: string;
  }>;
  action_script: ActionScript;
  correlation_id: string;
}

export interface SparringTurnResult {
  status: "success" | "error";
  session_id: string;
  user_message_id: string;
  assistant_message_id: string;
  philosophy_lens: string;
  response: string;
  matched_unit_ids: string[];
  citations: KnowledgeUnitCitation[];
  latency_ms: number;
}

export interface CouncilDeliberation {
  session_id: string;
  scenario_text: string;
  pitches: Array<{
    agent_id: string;
    title: string;
    stance: string;
    core_arguments: string[];
    cited_unit_ids: string[];
    risk_warning: string;
  }>;
  cross_debates: Array<{
    challenger_id: string;
    target_id: string;
    critique: string;
    counter_recommendation: string;
  }>;
  decision_matrix: {
    highest_consensus: string;
    core_conflicts: string[];
    plan_a_primary: { name: string; summary: string; action_steps: string[] };
    plan_b_fallback: { name: string; summary: string; action_steps: string[] };
    plan_c_containment: { name: string; summary: string; action_steps: string[] };
    critical_caveats: string[];
    execution_directives: string[];
  };
  total_latency_ms: number;
}

export class NhanThuatClient {
  private baseUrl: string;
  private apiKey?: string;
  private timeoutMs: number;

  constructor(config: NhanThuatClientConfig = {}) {
    this.baseUrl = (config.baseUrl || "http://127.0.0.1:8000").replace(/\/$/, "");
    this.apiKey = config.apiKey;
    this.timeoutMs = config.timeoutMs || 30000;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`NhanThuat API Error [${response.status}]: ${errorText}`);
      }

      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        return (await response.json()) as T;
      }
      return (await response.text()) as unknown as T;
    } finally {
      clearTimeout(timer);
    }
  }

  /** Analyze an operational scenario and obtain a structured 3-step action script. */
  async analyzeScenario(scenarioText: string, scenarioType: string = "general"): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>("/api/v1/nhan-thuat/analyze", {
      method: "POST",
      body: JSON.stringify({ scenario_text: scenarioText, scenario_type: scenarioType }),
    });
  }

  /** Start a stateful adversarial sparring session. */
  async startSparringSession(title: string, philosophyLens: string = "auto", context?: string): Promise<{ status: string; session: any }> {
    return this.request<{ status: string; session: any }>("/api/v1/sparring/sessions", {
      method: "POST",
      body: JSON.stringify({ title, philosophy_lens: philosophyLens, context }),
    });
  }

  /** Send a user message in an active sparring session. */
  async sendSparringMessage(sessionId: string, message: string, philosophyLens?: string): Promise<SparringTurnResult> {
    return this.request<SparringTurnResult>("/api/v1/sparring/messages", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, message, philosophy_lens: philosophyLens }),
    });
  }

  /** Trigger 5-Agent Philosophical Advisory Council deliberation. */
  async deliberateCouncil(scenarioText: string): Promise<{ status: string; deliberation: CouncilDeliberation }> {
    return this.request<{ status: string; deliberation: CouncilDeliberation }>("/api/v1/council/deliberate", {
      method: "POST",
      body: JSON.stringify({ scenario_text: scenarioText }),
    });
  }

  /** Export an executive decision brief as Markdown or Standalone Printable HTML. */
  async exportBrief(payload: {
    title: string;
    situation_summary: string;
    philosophy_analysis: string;
    action_script: Record<string, any>;
    knowledge_units?: Array<Record<string, any>>;
    directives?: string[];
    format?: "markdown" | "html";
  }): Promise<string> {
    return this.request<string>("/api/v1/export/brief", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }
}
