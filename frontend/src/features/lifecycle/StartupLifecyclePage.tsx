import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/common/Button";
import { environment } from "@/config/environment";
import { useAuth } from "@/features/auth/AuthContext";
import {
  lifecycleApi,
  type FinancialPlan,
  type LifecycleMilestoneResponse,
  type LifecycleRiskAssessment,
  type ProfileSuggestionReply,
  type StartupProfilePayload,
  type StartupProfileResponse,
} from "./lifecycle.api";
import { competitorApi, type CompetitorSearchResult } from "./competitor.api";

type Profile = {
  businessName: string;
  category: string;
  description: string;
  customers: string;
  country: string;
  district: string;
  city: string;
  investment: string;
  budget: string;
  experience: string;
  goals: string;
  industry: string;
  size: string;
  startupType: string;
  partners: string;
  employees: string;
  timeline: string;
};

const draftKey = "venturemind.lifecycle-profile-draft";
const trackerKey = "venturemind.lifecycle-progress";
const blank: Profile = {
  businessName: "",
  category: "",
  description: "",
  customers: "",
  country: "Sri Lanka",
  district: "",
  city: "",
  investment: "",
  budget: "",
  experience: "",
  goals: "",
  industry: "",
  size: "Micro",
  startupType: "New venture",
  partners: "1",
  employees: "0",
  timeline: "",
};
const milestones = [
  ["idea_created", "Idea Created"],
  ["risk_analysis", "Risk Analysis Completed"],
  ["business_registered", "Business Registered"],
  ["tax_registered", "Tax Registered"],
  ["licenses_approved", "Licences Approved"],
  ["brand_created", "Brand Identity Created"],
  ["website_created", "Website Created"],
  ["employees_hired", "Employees Hired"],
  ["marketing_started", "Marketing Started"],
  ["business_opened", "Business Opened"],
] as const;
const steps: Array<[string, Array<keyof Profile>]> = [
  ["Business identity", ["businessName", "category"]],
  ["Customer and location", ["description", "customers", "country", "district", "city"]],
  ["Funding and team", []],
  ["Goals and timeline", ["goals", "timeline"]],
] as const;
const profileFieldLabels: Record<keyof Profile, string> = {
  businessName: "Business name",
  category: "Business category",
  description: "Business description",
  customers: "Target customers",
  country: "Country",
  district: "District",
  city: "City or district",
  investment: "Expected investment",
  budget: "Available budget",
  experience: "Business experience",
  goals: "Business goals",
  industry: "Preferred industry",
  size: "Business size",
  startupType: "Startup type",
  partners: "Number of partners",
  employees: "Expected employees",
  timeline: "Launch timeline",
};
const countryOptions = ["Sri Lanka", "India", "Singapore", "United Kingdom", "United States", "Australia", "Other"];
const businessSizeOptions = ["Micro", "Small", "Medium", "Large"];
const partnerOptions = Array.from({ length: 10 }, (_, index) => String(index + 1));

function loadProfile(): Profile {
  try {
    return { ...blank, ...JSON.parse(localStorage.getItem(draftKey) ?? "{}") } as Profile;
  } catch {
    return blank;
  }
}

function loadProgress(): boolean[] {
  try {
    const stored = JSON.parse(localStorage.getItem(trackerKey) ?? "[]") as boolean[];
    return milestones.map((_, index) => Boolean(stored[index]));
  } catch {
    return milestones.map(() => false);
  }
}

function asOptional(value: string): string | null {
  return value.trim() || null;
}
function asNumber(value: string, fallback = 0): number {
  const result = Number(value);
  return Number.isFinite(result) ? result : fallback;
}
function formatLkr(value: unknown): string {
  const amount = Number(value);
  return Number.isFinite(amount)
    ? new Intl.NumberFormat("en-LK", { style: "currency", currency: "LKR", maximumFractionDigits: 0 }).format(amount)
    : "Not reached";
}

function toPayload(profile: Profile): StartupProfilePayload {
  return {
    business_name: profile.businessName.trim(),
    category: profile.category.trim(),
    description: profile.description.trim(),
    industry: asOptional(profile.industry),
    target_customers: asOptional(profile.customers),
    country: asOptional(profile.country),
    district: asOptional(profile.district),
    city: asOptional(profile.city),
    expected_investment: profile.investment.trim() ? asNumber(profile.investment) : null,
    available_budget: profile.budget.trim() ? asNumber(profile.budget) : null,
    business_experience: asOptional(profile.experience),
    business_goals: asOptional(profile.goals),
    business_size: asOptional(profile.size),
    startup_type: asOptional(profile.startupType),
    partner_count: Math.max(1, asNumber(profile.partners, 1)),
    expected_employees: Math.max(0, asNumber(profile.employees)),
    launch_timeline: asOptional(profile.timeline),
  };
}

function fromApi(profile: StartupProfileResponse): Profile {
  return {
    businessName: profile.business_name,
    category: profile.category,
    description: profile.description,
    customers: profile.target_customers ?? "",
    country: profile.country ?? "",
    district: profile.district ?? "",
    city: profile.city ?? "",
    investment: profile.expected_investment?.toString() ?? "",
    budget: profile.available_budget?.toString() ?? "",
    experience: profile.business_experience ?? "",
    goals: profile.business_goals ?? "",
    industry: profile.industry ?? "",
    size: profile.business_size ?? "Micro",
    startupType: profile.startup_type ?? "New venture",
    partners: profile.partner_count.toString(),
    employees: profile.expected_employees.toString(),
    timeline: profile.launch_timeline ?? "",
  };
}

export function StartupLifecyclePage() {
  const { isAuthenticated } = useAuth();
  const [profile, setProfile] = useState<Profile>(loadProfile);
  const [step, setStep] = useState(0);
  const [saved, setSaved] = useState(false);
  const [progress, setProgress] = useState<boolean[]>(loadProgress);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState("");
  const [profileFinished, setProfileFinished] = useState(false);
  const [profileSuggestions, setProfileSuggestions] = useState<ProfileSuggestionReply | null>(null);
  const [profileAssistantOpen, setProfileAssistantOpen] = useState(false);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [suggestionsError, setSuggestionsError] = useState("");
  const [competitorResult, setCompetitorResult] = useState<CompetitorSearchResult | null>(null);
  const [competitorLoading, setCompetitorLoading] = useState(false);
  const [competitorError, setCompetitorError] = useState("");
  const [showAllCompetitors, setShowAllCompetitors] = useState(false);
  const [riskAssessment, setRiskAssessment] = useState<LifecycleRiskAssessment | null>(null);
  const [riskLoading, setRiskLoading] = useState(false);
  const [riskError, setRiskError] = useState("");
  const [riskDetailsOpen, setRiskDetailsOpen] = useState(false);
  const [financialPlan, setFinancialPlan] = useState<FinancialPlan | null>(null);
  const [financialLoading, setFinancialLoading] = useState(false);
  const [financialError, setFinancialError] = useState("");
  const [financialInputs, setFinancialInputs] = useState({
    rent: "",
    utilities: "",
    salaries: "",
    marketing: "",
    softwareDelivery: "",
    loan: "",
    other: "",
    setup: "",
    emergency: "",
    sales: "",
    averageSale: "",
    revenue: "",
    margin: "50",
  });
  const [advisorQuestion, setAdvisorQuestion] = useState("What should I validate first before launching?");
  const [advisorReply, setAdvisorReply] = useState<{ response: string; mode: string } | null>(null);
  const [advisorLoading, setAdvisorLoading] = useState(false);
  const [advisorConversationId, setAdvisorConversationId] = useState<string | undefined>();
  const backendEnabled = !environment.demoMode && isAuthenticated;
  const completed = progress.filter(Boolean).length;
  const percent = Math.round((completed / milestones.length) * 100);
  const hasIdentity = Boolean(profile.businessName.trim() && profile.category.trim() && profile.description.trim());
  const profileRequirements = [
    ["Business name", profile.businessName],
    ["Business category", profile.category],
    ["Business description", profile.description],
    ["Target customers", profile.customers],
    ["Country", profile.country],
    ["City or district", profile.city || profile.district],
    ["Business goals", profile.goals],
    ["Launch timeline", profile.timeline],
  ] as const;
  const missingProfileFields = profileRequirements.filter(([, value]) => !value.trim()).map(([label]) => label);
  const profileReadiness = Math.round(
    ((profileRequirements.length - missingProfileFields.length) / profileRequirements.length) * 100,
  );
  const profileReady = profileFinished || missingProfileFields.length === 0;
  const missingFieldsForStep = (stepIndex: number) => {
    const fields = steps[stepIndex][1];
    const missing = fields
      .filter((key) => key !== "city" && key !== "district" && !profile[key].trim())
      .map((key) => profileFieldLabels[key]);
    if (fields.includes("city") && fields.includes("district") && !profile.city.trim() && !profile.district.trim())
      missing.push("City or district");
    return missing;
  };
  const currentStepMissingFields = missingFieldsForStep(step);
  const summary = useMemo(
    () =>
      `${profile.businessName || "Your startup"} is a ${profile.size.toLowerCase()} ${profile.startupType.toLowerCase()} in ${profile.city || profile.country || "your chosen market"}.`,
    [profile],
  );
  const workspaceStages = [
    {
      number: 1,
      title: "Complete startup profile",
      detail: "Describe your business, customers, location, budget, and launch goal.",
      done: profileReady,
      action: "Complete profile",
      target: "#startup-profile",
      reason: missingProfileFields.length
        ? `${missingProfileFields.length} required profile fields still need details.`
        : "",
    },
    {
      number: 2,
      title: "Assess risks and competitors",
      detail: "Check risk evidence and review nearby businesses in your market.",
      done: Boolean(riskAssessment),
      action: "Run analysis",
      target: "#risk-analysis",
      reason: profileReady ? "" : "Complete your profile first.",
    },
    {
      number: 3,
      title: "Create a financial plan",
      detail: "Estimate monthly costs, revenue, funding needs, and break-even point.",
      done: Boolean(financialPlan),
      action: "Plan finances",
      target: "#financial-plan",
      reason: riskAssessment ? "" : "Complete risk analysis first.",
    },
    {
      number: 4,
      title: "Register, launch, and grow",
      detail: "Follow legal guidance, speak to an advisor, and track delivery milestones.",
      done:
        profileReady &&
        Boolean(riskAssessment) &&
        Boolean(financialPlan) &&
        Boolean(progress[milestones.findIndex(([key]) => key === "business_opened")]),
      action: "Continue launch",
      target: "#legal-checklist",
      reason: financialPlan ? "Complete legal and launch actions to finish this step." : "Finish your financial plan first.",
    },
  ];
  const nextWorkspaceStage = workspaceStages.find((item) => !item.done) ?? workspaceStages[workspaceStages.length - 1];

  useEffect(() => {
    const target = window.location.hash;
    const sectionText: Record<string, string> = {
      "#startup-profile": "Startup profile",
      "#risk-analysis": "AI startup risk analysis",
      "#financial-plan": "Investment planner",
      "#legal-checklist": "Sri Lanka legal checklist",
    };
    if (!target || !sectionText[target]) return;
    const frame = window.requestAnimationFrame(() => {
      const section =
        document.querySelector(target) ??
        Array.from(document.querySelectorAll("section")).find((item) =>
          item.textContent?.includes(sectionText[target]),
        );
      section?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);

  const persistLocal = (nextProfile = profile, nextProgress = progress) => {
    localStorage.setItem(draftKey, JSON.stringify(nextProfile));
    localStorage.setItem(trackerKey, JSON.stringify(nextProgress));
    localStorage.setItem("venturemind.lifecycle-profile-last-saved", new Date().toISOString());
    window.dispatchEvent(new Event("venturemind-profile-saved"));
  };

  const applyMilestones = (items: LifecycleMilestoneResponse[]) => {
    const byKey = new Map(items.map((item) => [item.milestone_key, Boolean(item.completed_at)]));
    const next = milestones.map(([key]) => byKey.get(key) ?? false);
    setProgress(next);
    persistLocal(profile, next);
  };

  useEffect(() => {
    if (!backendEnabled) return;
    let active = true;
    setSyncing(true);
    lifecycleApi
      .listProfiles()
      .then(async (items) => {
        if (!active || !items[0]) return;
        const remote = items[0];
        setProfileId(remote.id);
        const restored = fromApi(remote);
        setProfile(restored);
        localStorage.setItem(draftKey, JSON.stringify(restored));
        const remoteMilestones = await lifecycleApi.listMilestones(remote.id);
        if (active) {
          const byKey = new Map(remoteMilestones.map((item) => [item.milestone_key, Boolean(item.completed_at)]));
          const next = milestones.map(([key]) => byKey.get(key) ?? false);
          setProgress(next);
          localStorage.setItem(trackerKey, JSON.stringify(next));
        }
        try {
          const savedRisk = await lifecycleApi.latestRiskAssessment(remote.id);
          if (active) setRiskAssessment(savedRisk);
        } catch {
          /* A profile without a previous assessment is expected. */
        }
        try {
          const savedPlan = await lifecycleApi.latestFinancialPlan(remote.id);
          if (!active) return;
          setFinancialPlan(savedPlan);
          const assumptions = savedPlan.assumptions;
          const value = (key: string, fallback = "") => String(assumptions[key] ?? fallback);
          setFinancialInputs({
            rent: value("monthly_rent"), utilities: value("monthly_utilities_cost"),
            salaries: value("monthly_salary_cost"), marketing: value("monthly_marketing_cost"),
            softwareDelivery: value("monthly_software_delivery_cost"), loan: value("monthly_loan_repayment"),
            other: value("monthly_other_cost"), setup: value("one_time_setup_cost"),
            emergency: value("emergency_fund"), sales: value("expected_monthly_sales"),
            averageSale: value("average_sale_value"), revenue: value("expected_monthly_revenue"),
            margin: value("gross_margin_percent", "50"),
          });
        } catch {
          /* A profile without a saved financial plan is expected. */
        }
      })
      .catch(() => {
        if (active) setSyncMessage("Cloud workspace could not be loaded. Your local draft remains safe.");
      })
      .finally(() => {
        if (active) setSyncing(false);
      });
    return () => {
      active = false;
    };
  }, [backendEnabled]);

  const update = (key: keyof Profile, value: string) => {
    setProfile((current) => ({ ...current, [key]: value }));
    setProfileFinished(false);
    setSaved(false);
    setSyncMessage("");
  };

  const suggestProfileFields = async () => {
    if (!profile.businessName.trim() || !profile.category.trim()) return;
    setSuggestionsLoading(true);
    setSuggestionsError("");
    try {
      const result = await lifecycleApi.suggestProfileFields({
        business_name: profile.businessName.trim(),
        category: profile.category.trim(),
        country: asOptional(profile.country),
        city: asOptional(profile.city),
      });
      setProfileSuggestions(result);
      setProfileAssistantOpen(true);
    } catch {
      setSuggestionsError("Could not get suggestions. Check your backend connection and try again.");
    } finally {
      setSuggestionsLoading(false);
    }
  };

  const applySuggestion = (key: "industry" | "startup_type" | "target_customers" | "description", value: string) => {
    const profileKey: Record<typeof key, keyof Profile> = {
      industry: "industry",
      startup_type: "startupType",
      target_customers: "customers",
      description: "description",
    };
    update(profileKey[key], value);
  };

  const save = async (complete = false) => {
    persistLocal();
    setSaved(true);
    if (complete && missingProfileFields.length) {
      setSyncMessage(
        `Complete these required fields before finishing your profile: ${missingProfileFields.join(", ")}.`,
      );
      return;
    }
    if (!backendEnabled) {
      if (complete) setProfileFinished(true);
      setSyncMessage(
        complete
          ? "Profile completed and saved on this device. It will remain after refresh so you can continue planning."
          : "Saved on this device. Sign in with demo mode disabled to save to your account.",
      );
      return;
    }
    if (!hasIdentity) {
      setSyncMessage("Add a business name, category, and description before saving to your account.");
      return;
    }
    setSyncing(true);
    try {
      const remote = profileId
        ? await lifecycleApi.updateProfile(profileId, toPayload(profile))
        : await lifecycleApi.createProfile(toPayload(profile));
      setProfileId(remote.id);
      if (complete) {
        setProfileFinished(true);
        await lifecycleApi.updateMilestone(remote.id, "idea_created", true).catch(() => undefined);
      }
      setSyncMessage(
        complete
          ? "Profile completed and saved securely to your VentureMind workspace."
          : "Saved securely to your VentureMind workspace.",
      );
      applyMilestones(await lifecycleApi.listMilestones(remote.id));
    } catch {
      setSyncMessage("Could not save to the server. Your local draft is still saved on this device.");
    } finally {
      setSyncing(false);
    }
  };

  const toggle = async (index: number) => {
    const next = progress.map((value, itemIndex) => (itemIndex === index ? !value : value));
    setProgress(next);
    persistLocal(profile, next);
    if (!backendEnabled || !profileId) return;
    setSyncing(true);
    try {
      await lifecycleApi.updateMilestone(profileId, milestones[index][0], next[index]);
      setSyncMessage("Progress saved to your workspace.");
    } catch {
      setSyncMessage("Progress was saved locally but could not be synced to the server.");
    } finally {
      setSyncing(false);
    }
  };

  const searchCompetitors = async () => {
    setCompetitorError("");
    if (!profile.category.trim()) {
      setCompetitorError("Add a business category first, for example “Food and beverage”.");
      return;
    }
    if (!backendEnabled) {
      setCompetitorError(
        "Sign in with demo mode disabled to load listings inside VentureMind. You can still use the live Maps link below.",
      );
      return;
    }
    setCompetitorLoading(true);
    try {
      setCompetitorResult(
        await competitorApi.search({
          business_category: profile.category,
          industry: asOptional(profile.industry),
          city: asOptional(profile.city),
          district: asOptional(profile.district),
          country: profile.country || "Sri Lanka",
          max_results: 5,
        }),
      );
    } catch {
      setCompetitorError(
        "In-app competitor listings are not available yet. Use Google Maps below to research real nearby businesses.",
      );
    } finally {
      setCompetitorLoading(false);
    }
  };

  const buildStructuredRiskAssessment = (): LifecycleRiskAssessment => {
    const hasLocation = Boolean(profile.city.trim() || profile.district.trim());
    const investment = Number(profile.investment) || 0;
    const budget = Number(profile.budget) || 0;
    const hasBudget = investment > 0 && budget > 0;
    const budgetCoverage = hasBudget && budget >= investment * 0.5;
    const detailedDescription = profile.description.trim().length >= 120;
    const detailedCustomer = profile.customers.trim().length >= 80;
    const content =
      `${profile.description} ${profile.customers} ${profile.goals} ${profile.industry} ${profile.startupType}`.toLowerCase();
    const hasTerms = (terms: string[]) => terms.some((term) => content.includes(term));
    const demandEvidence = hasTerms([
      "interview",
      "survey",
      "demand",
      "pre-order",
      "customer feedback",
      "willingness to pay",
    ]);
    const differentiation = hasTerms([
      "unique",
      "faster",
      "affordable",
      "convenient",
      "specialised",
      "different",
      "gap",
    ]);
    const operationalEvidence = hasTerms(["supplier", "delivery", "inventory", "process", "equipment", "workflow"]);
    const regulated = hasTerms(["food", "health", "medical", "finance", "transport", "tourism", "import", "education"]);
    const card = (key: string, label: string, base: number, checks: Array<[boolean, number, string]>, next: string) => {
      const positive_factors = checks.filter(([passed]) => passed).map(([, , message]) => message);
      const negative_factors = checks
        .filter(([passed]) => !passed)
        .map(([, , message]) => `Missing evidence: ${message}`);
      const risk_score = Math.max(
        5,
        Math.min(95, base - checks.filter(([passed]) => passed).reduce((total, [, points]) => total + points, 0)),
      );
      return {
        key,
        label,
        risk_score,
        reasoning: `This score is calculated from the saved ${label.toLowerCase()} evidence in this profile.`,
        positive_factors,
        negative_factors,
        suggestions: [next],
      };
    };
    const scorecards = [
      card(
        "market_risk",
        "Market risk",
        82,
        [
          [detailedDescription, 18, "The business offer is described in detail."],
          [hasLocation, 12, "A target location is specified."],
          [Boolean(profile.industry.trim()), 8, "An industry is specified."],
          [demandEvidence, 14, "Customer-demand evidence is recorded."],
        ],
        "Interview target customers and validate local demand.",
      ),
      card(
        "financial_risk",
        "Financial risk",
        88,
        [
          [investment > 0, 20, "Expected investment is recorded."],
          [budget > 0, 20, "Available budget is recorded."],
          [budgetCoverage, 20, "Available budget covers at least half of expected investment."],
        ],
        "Record startup costs, expected sales, and a monthly cash-flow plan.",
      ),
      card(
        "competition_risk",
        "Competition risk",
        78,
        [
          [hasLocation, 18, "A competitor-search location is available."],
          [detailedDescription, 12, "The offer is detailed enough to compare."],
          [Boolean(profile.category.trim()), 12, "A business category is specified."],
          [differentiation, 12, "A differentiation claim is documented."],
        ],
        "Compare nearby competitors, pricing, and the gap you can serve.",
      ),
      card(
        "customer_risk",
        "Customer risk",
        84,
        [
          [detailedCustomer, 24, "Target customers are described in detail."],
          [profile.goals.trim().length >= 60, 12, "Business goals are documented."],
          [demandEvidence, 16, "Customer-validation evidence is recorded."],
        ],
        "Define a narrow target customer and test willingness to pay.",
      ),
      card(
        "operational_risk",
        "Operational risk",
        80,
        [
          [Boolean(profile.experience.trim()), 18, "Founder experience is documented."],
          [profile.employees !== "0", 12, "Expected staffing is planned."],
          [Boolean(profile.timeline.trim()), 14, "A launch timeline is defined."],
          [operationalEvidence, 12, "Operational delivery evidence is recorded."],
        ],
        "Define suppliers, roles, operating steps, and launch timing.",
      ),
      card(
        "legal_risk",
        "Legal risk",
        86,
        [
          [Boolean(profile.country.trim()), 16, "Country is recorded for legal guidance."],
          [hasLocation, 10, "Local authority area is recorded."],
          [regulated, 8, "The profile identifies a regulated-sector requirement."],
        ],
        "Confirm registrations, licences, taxes, and local approvals.",
      ),
      card(
        "scalability_risk",
        "Scalability risk",
        79,
        [
          [
            hasTerms(["digital", "platform", "software", "online", "subscription", "automation"]),
            25,
            "Digital or repeatable delivery signals are present.",
          ],
          [profile.partners !== "1", 8, "More than one partner is planned."],
          [profile.employees !== "0", 8, "A team plan is recorded."],
        ],
        "Document repeatable processes before growing the team.",
      ),
    ];
    const overall_risk_score = Math.round(
      scorecards.reduce((total, item) => total + item.risk_score, 0) / scorecards.length,
    );
    const business_confidence_score = 100 - overall_risk_score;
    return {
      id: "local-risk-assessment",
      startup_profile_id: profileId ?? "local-profile",
      overall_success_score: Math.round(business_confidence_score * 0.8),
      business_confidence_score,
      overall_risk_score,
      risk_level: overall_risk_score >= 70 ? "high" : overall_risk_score >= 45 ? "moderate" : "low",
      methodology_version: "structured-local-risk-v1",
      scorecards,
      recommendations: scorecards
        .sort((a, b) => b.risk_score - a.risk_score)
        .slice(0, 3)
        .map((item, index) => ({
          priority: index === 0 ? "high" : "medium",
          metric: item.key,
          recommendation: item.suggestions[0],
        })),
    };
  };

  const analyseRisk = async () => {
    setRiskError("");
    setRiskDetailsOpen(false);
    setRiskLoading(true);
    try {
      if (backendEnabled && profileId) {
        setRiskAssessment(await lifecycleApi.createRiskAssessment(profileId));
        setSyncMessage("Risk analysis saved to your VentureMind workspace.");
      } else {
        setRiskAssessment(buildStructuredRiskAssessment());
      }
    } catch (error) {
      // A successful POST can be persisted even if a stale client receives an
      // unexpected response shape. Confirm the saved result before showing a
      // misleading local-only fallback.
      if (backendEnabled && profileId) {
        try {
          const savedAssessment = await lifecycleApi.latestRiskAssessment(profileId);
          setRiskAssessment(savedAssessment);
          setRiskError("");
          setSyncMessage("Risk analysis was saved and reloaded from your VentureMind workspace.");
          return;
        } catch {
          console.error("Risk analysis could not be recovered from the server.", error);
        }
      }
      setRiskAssessment(buildStructuredRiskAssessment());
      setRiskError(
        "The analysis is shown locally, but it was not saved. Update the backend database migration (ai_explanation field), restart the API, then run the analysis again.",
      );
    } finally {
      setRiskLoading(false);
    }
  };

  const makeFinancialPlan = async () => {
    setFinancialError("");
    if (!backendEnabled || !profileId) {
      setFinancialError("Save your completed profile while signed in to generate a saved financial plan.");
      return;
    }
    const number = (value: string) => Number(value) || 0;
    if (
      number(financialInputs.revenue) <= 0 &&
      (number(financialInputs.sales) <= 0 || number(financialInputs.averageSale) <= 0)
    ) {
      setFinancialError("Enter expected monthly revenue, or enter both expected monthly sales and average sale value.");
      return;
    }
    setFinancialLoading(true);
    try {
      const plan = await lifecycleApi.createFinancialPlan(profileId, {
          partner_count: Number(profile.partners) || 1,
          monthly_rent: number(financialInputs.rent),
          monthly_salary_cost: number(financialInputs.salaries),
          monthly_marketing_cost: number(financialInputs.marketing),
          monthly_other_cost: number(financialInputs.other),
          monthly_utilities_cost: number(financialInputs.utilities),
          monthly_software_delivery_cost: number(financialInputs.softwareDelivery),
          monthly_loan_repayment: number(financialInputs.loan),
          one_time_setup_cost: number(financialInputs.setup),
          emergency_fund: number(financialInputs.emergency),
          expected_monthly_sales: number(financialInputs.sales),
          average_sale_value: number(financialInputs.averageSale),
          expected_monthly_revenue: number(financialInputs.revenue),
          gross_margin_percent: Math.min(99, Math.max(1, number(financialInputs.margin) || 50)),
        });
      setFinancialPlan(plan);
      setSyncMessage("Financial plan saved. Your dashboard will now use this forecast.");
      window.dispatchEvent(new Event("venturemind-profile-saved"));
    } catch {
      setFinancialError("Financial plan could not be saved. Confirm the backend is running, then try again.");
    } finally {
      setFinancialLoading(false);
    }
  };
  const showStructuredAdvice = () => {
    const startup = profile.businessName || "your startup";
    const location = profile.city || profile.district || profile.country || "your target market";
    setAdvisorReply({
      mode: "structured",
      response: `For ${startup}, start with a small customer-validation test in ${location}. Speak with 10 target customers about the problem, their current alternative, and willingness to pay. Then define one measurable MVP outcome before committing further budget. Your question was: “${advisorQuestion.trim()}”`,
    });
  };

  const askAdvisor = async () => {
    if (!advisorQuestion.trim()) return;
    setAdvisorLoading(true);
    try {
      if (backendEnabled && profileId) {
        const reply = await lifecycleApi.askAdvisor(profileId, advisorQuestion, advisorConversationId);
        setAdvisorReply(reply);
        setAdvisorConversationId(reply.conversation_id);
      } else showStructuredAdvice();
    } catch {
      showStructuredAdvice();
    } finally {
      setAdvisorLoading(false);
    }
  };

  const goToProfileStep = (nextStep: number) => {
    if (nextStep <= step) {
      setStep(nextStep);
      return;
    }
    for (let index = step; index < nextStep; index += 1) {
      const missing = missingFieldsForStep(index);
      if (missing.length) {
        setStep(index);
        setSyncMessage(`Complete the required fields in Step ${index + 1}: ${missing.join(", ")}.`);
        return;
      }
    }
    setSyncMessage("");
    setStep(nextStep);
  };

  const openWorkspaceSection = (target: string) => {
    const sectionText: Record<string, string> = {
      "#startup-profile": "Startup profile",
      "#risk-analysis": "AI startup risk analysis",
      "#financial-plan": "Investment planner",
      "#legal-checklist": "Sri Lanka legal checklist",
    };
    const section =
      document.querySelector(target) ??
      Array.from(document.querySelectorAll("section")).find((item) =>
        item.textContent?.includes(sectionText[target] ?? ""),
      );
    if (!section) return;
    window.history.replaceState(null, "", target);
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const field = (key: keyof Profile, label: string, placeholder = "", area = false, required = true) => (
    <label className="block text-sm font-semibold">
      {label}{" "}
      {required ? <span className="text-rose-600" aria-hidden="true">*</span> : <span className="text-xs font-normal text-slate-500">Optional</span>}
      {area ? (
        <textarea
          value={profile[key]}
          onChange={(event) => update(key, event.target.value)}
          aria-required={required}
          className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal dark:border-slate-700"
          rows={4}
          placeholder={placeholder}
        />
      ) : (
        <input
          value={profile[key]}
          onChange={(event) => update(key, event.target.value)}
          aria-required={required}
          className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal dark:border-slate-700"
          placeholder={placeholder}
        />
      )}
    </label>
  );

  const selectField = (key: keyof Profile, label: string, options: string[], required = true) => (
    <label className="block text-sm font-semibold">
      {label}{" "}
      {required ? <span className="text-rose-600" aria-hidden="true">*</span> : <span className="text-xs font-normal text-slate-500">Optional</span>}
      <select
        value={profile[key]}
        onChange={(event) => update(key, event.target.value)}
        aria-required={required}
        className="mt-2 w-full rounded-lg border border-slate-300 bg-transparent p-3 font-normal dark:border-slate-700"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );

  const competitorSearch = [
    profile.category || profile.industry || "businesses",
    profile.city || profile.district,
    profile.country,
  ]
    .filter(Boolean)
    .join(" near ");
  const competitorSearchUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(competitorSearch)}`;

  return (
    <div className="mx-auto max-w-7xl">
      <section className="rounded-3xl bg-slate-950 px-6 py-10 text-white sm:px-10">
        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div>
            <p className="text-sm font-bold uppercase tracking-widest text-accent-300">Founder workspace</p>
            <h1 className="mt-3 text-3xl font-bold sm:text-4xl">Build your startup, one clear step at a time.</h1>
            <p className="mt-3 max-w-3xl leading-7 text-slate-300">
              Complete each stage in order. VentureMind keeps your profile, analysis, plan, and launch progress together
              in one place.
            </p>
          </div>
          <div className="rounded-2xl bg-white/10 px-5 py-4 text-sm">
            <p className="font-bold text-accent-200">Your next step</p>
            <p className="mt-1 text-lg font-bold">
              {nextWorkspaceStage.number}. {nextWorkspaceStage.title}
            </p>
            <p className="mt-1 text-slate-300">{nextWorkspaceStage.action} below</p>
          </div>
        </div>
      </section>
      <section className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-4" aria-label="Startup workspace journey">
        {workspaceStages.map((stage) => (
          <button
            type="button"
            key={stage.number}
            onClick={() => openWorkspaceSection(stage.target)}
            className={`rounded-2xl border p-4 text-left transition hover:-translate-y-0.5 hover:shadow-card ${stage.number === nextWorkspaceStage.number ? "border-brand-400 bg-brand-50/70 shadow-card dark:border-brand-500 dark:bg-brand-500/10" : "border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900"}`}
          >
            <div className="flex items-center justify-between gap-3">
              <span
                className={`grid h-8 w-8 place-items-center rounded-full text-sm font-extrabold ${stage.done ? "bg-emerald-100 text-emerald-700" : "bg-brand-600 text-white"}`}
              >
                {stage.done ? "✓" : stage.number}
              </span>
              <span
                className={`text-xs font-bold ${stage.done ? "text-emerald-700" : stage.number === nextWorkspaceStage.number ? "text-brand-700 dark:text-brand-300" : "text-slate-500"}`}
              >
                {stage.done ? "Complete" : stage.number === nextWorkspaceStage.number ? "DO THIS NEXT" : "UPCOMING"}
              </span>
            </div>
            <h2 className="mt-3 font-bold">{stage.title}</h2>
            <p className="mt-1 text-sm leading-5 text-slate-600 dark:text-slate-300">{stage.detail}</p>
            {stage.reason && (
              <p className="mt-3 text-xs font-medium text-amber-700 dark:text-amber-300">{stage.reason}</p>
            )}
          </button>
        ))}
      </section>
      <div className="mt-8 space-y-8">
        <section
          id="startup-profile"
          className="mx-auto max-w-5xl rounded-3xl border border-slate-200 bg-white p-5 shadow-card sm:p-7 dark:border-slate-800 dark:bg-slate-900"
        >
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
            <div>
              <p className="text-sm font-bold uppercase tracking-widest text-brand-600">Startup profile</p>
              <h2 className="mt-1 text-2xl font-bold">
                Step {step + 1}: {steps[step][0]}
              </h2>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Only the essentials are required. You can return and improve the rest later.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-bold text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">
                {backendEnabled ? (syncing ? "Syncing…" : "Cloud workspace") : "Local draft"}
              </span>
              <Button variant="secondary" onClick={() => setProfileAssistantOpen((open) => !open)}>
                {profileAssistantOpen ? "Hide AI helper" : "AI profile helper"}
              </Button>
            </div>
          </div>
          {syncMessage && (
            <p
              className="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-600 dark:bg-slate-800 dark:text-slate-300"
              role="status"
            >
              {syncMessage}
            </p>
          )}
          <div className="mt-6 flex flex-wrap gap-2 border-y border-slate-100 py-3 dark:border-slate-800">
            {steps.map(([title], index) => (
              <button
                key={title}
                className={`rounded-full border px-3 py-2 text-left transition ${index === step ? "border-brand-500 bg-brand-50 text-brand-900 dark:bg-brand-500/10 dark:text-brand-100" : index < step ? "border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-900 dark:bg-emerald-950/20 dark:text-emerald-100" : "border-slate-200 text-slate-500 hover:border-brand-300 dark:border-slate-800 dark:text-slate-400"}`}
                onClick={() => goToProfileStep(index)}
              >
                <span className="text-xs font-extrabold">{index < step ? "✓" : index + 1}</span>
                <span className="ml-1.5 text-sm font-bold">{title}</span>
              </button>
            ))}
          </div>
          <div className="mx-auto mt-6 max-w-3xl space-y-5">
            {step === 0 && (
              <>
                <div className="grid gap-5 sm:grid-cols-2">
                  {field("businessName", "Business name", "Example: NorthStar Foods")}
                  {field("category", "Business category", "Example: Food and beverage")}
                </div>
                {profileAssistantOpen && <div className="mt-4 rounded-2xl border border-brand-100 bg-brand-50/60 p-4 dark:border-brand-500/30 dark:bg-brand-500/10">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="font-bold text-brand-800 dark:text-brand-200">AI Profile Assistant</p>
                      <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                        Optional editable ideas for completing your profile. Nothing is saved automatically.
                      </p>
                    </div>
                    <Button variant="secondary" onClick={() => setProfileAssistantOpen(false)}>
                      Hide assistant
                    </Button>
                  </div>
                    <div className="mt-4 border-t border-brand-100 pt-4 dark:border-brand-500/30">
                      <Button
                        disabled={suggestionsLoading || !profile.businessName.trim() || !profile.category.trim()}
                        onClick={() => void suggestProfileFields()}
                      >
                        {suggestionsLoading ? "Suggesting..." : "Suggest profile details"}
                      </Button>
                      {!profile.businessName.trim() || !profile.category.trim() ? (
                        <p className="mt-3 text-sm text-amber-800 dark:text-amber-200">
                          Add a business name and category first, then VentureMind can suggest draft profile details.
                        </p>
                      ) : null}
                      {suggestionsError && <p className="mt-3 text-sm text-rose-600">{suggestionsError}</p>}
                      {profileSuggestions && (
                        <div className="mt-4">
                          <p className="text-xs font-bold uppercase tracking-wider text-brand-700 dark:text-brand-300">
                            {profileSuggestions.mode === "gemini" ? "Gemini suggestions" : "Structured suggestions"}
                          </p>
                          <p className="mt-1 text-xs text-slate-500">{profileSuggestions.notice}</p>
                          <div className="mt-3 grid gap-3 sm:grid-cols-2">
                            {(
                              [
                                ["industry", "Preferred industry"],
                                ["startup_type", "Startup type"],
                                ["target_customers", "Target customers"],
                                ["description", "Business description"],
                              ] as const
                            ).map(([key, label]) => (
                              <article key={key} className="rounded-lg bg-white p-3 shadow-sm dark:bg-slate-900">
                                <p className="text-xs font-bold text-slate-500">{label}</p>
                                <p className="mt-1 text-sm">{profileSuggestions.suggestions[key]}</p>
                                <button
                                  className="mt-3 text-sm font-bold text-brand-700 hover:underline dark:text-brand-300"
                                  onClick={() => applySuggestion(key, profileSuggestions.suggestions[key])}
                                >
                                  Use suggestion
                                </button>
                              </article>
                            ))}
                          </div>
                          <p className="mt-3 text-sm font-medium text-slate-700 dark:text-slate-200">
                            Next question: {profileSuggestions.suggestions.next_question}
                          </p>
                        </div>
                      )}
                    </div>
                </div>}
                <div className="grid gap-5 sm:grid-cols-2">
                  {field("industry", "Preferred industry", "Example: Retail", false, false)}
                  {field("startupType", "Startup type", "Example: New venture", false, false)}
                </div>
              </>
            )}
            {step === 1 && (
              <>
                {field(
                  "description",
                  "Business description",
                  "What will the business offer and why does it matter?",
                  true,
                )}
                {field("customers", "Target customers", "Who will buy from you and what do they need?", true)}
                <div className="grid gap-5 sm:grid-cols-3">
                  {selectField("country", "Country", countryOptions)}
                  {field("district", "District", "Example: Jaffna")}
                  {field("city", "City")}
                </div>
              </>
            )}
            {step === 2 && (
              <>
                <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  Optional planning details. Add them now for more tailored risk and financial guidance, or save them later.
                </p>
                <div className="mt-5 grid gap-5 sm:grid-cols-2">
                  {field("investment", "Expected investment", "Example: 500000 LKR", false, false)}
                  {field("budget", "Available budget", "Example: 300000 LKR", false, false)}
                  {field("experience", "Business experience", "Example: Two years in retail", false, false)}
                  {selectField("size", "Business size", businessSizeOptions, false)}
                  {selectField("partners", "Number of partners", partnerOptions, false)}
                  {field("employees", "Expected employees", "Example: 2", false, false)}
                </div>
              </>
            )}
            {step === 3 && (
              <>
                {field("goals", "Business goals", "What should this business achieve in its first year?", true)}
                {field("timeline", "Launch timeline", "Example: Open within six months")}
              </>
            )}
          </div>
          {currentStepMissingFields.length > 0 && (
            <p className="mt-5 rounded-lg bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/30 dark:text-amber-100">
              Complete the required fields in this step before continuing: {currentStepMissingFields.join(", ")}.
            </p>
          )}
          <div className="mt-8 flex flex-wrap justify-between gap-3 border-t border-slate-100 pt-5 dark:border-slate-800">
            <Button variant="secondary" disabled={step === 0} onClick={() => setStep((current) => current - 1)}>
              Back
            </Button>
            <div className="flex gap-3">
              <Button variant="secondary" disabled={syncing} onClick={() => void save()}>
                {saved ? "Draft saved" : "Save draft"}
              </Button>
              {step < steps.length - 1 ? (
                <Button disabled={currentStepMissingFields.length > 0} onClick={() => goToProfileStep(step + 1)}>
                  Continue
                </Button>
              ) : (
                <Button disabled={!profileReady || syncing} onClick={() => void save(true)}>
                  Finish profile
                </Button>
              )}
            </div>
          </div>
          {profileReady && (
            <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-950 dark:border-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-100">
              <p className="font-bold">Step 1 complete — your startup profile is ready.</p>
              <p className="mt-1">Next, use Step 2 below to run your risk analysis and competitor check.</p>
            </div>
          )}
        </section>
        <section className="rounded-2xl border border-brand-100 bg-brand-50/60 p-5 dark:border-brand-500/30 dark:bg-brand-500/10">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-bold text-brand-800 dark:text-brand-200">
                {workspaceStages.filter((stage) => stage.done).length} of 4 steps complete · Profile readiness:{" "}
                {profileReadiness}%
              </p>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                {missingProfileFields.length
                  ? `Add ${missingProfileFields.join(", ")} to unlock risk analysis.`
                  : "Your profile contains the required planning information."}
              </p>
            </div>
            <button
              className="text-sm font-bold text-brand-700 underline"
              onClick={() => {
                setStep(0);
                document.getElementById("startup-profile")?.scrollIntoView({ behavior: "smooth", block: "start" });
              }}
            >
              Edit profile
            </button>
          </div>
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-brand-100 dark:bg-slate-800">
            <div className="h-full rounded-full bg-brand-600" style={{ width: `${profileReadiness}%` }} />
          </div>
        </section>
        <section className="rounded-2xl bg-slate-950 p-5 text-white">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-accent-300">AI business advisor</p>
              <h2 className="mt-1 text-xl font-bold">Get contextual startup guidance</h2>
              <p className="mt-2 text-sm text-slate-300">
                Context used: Profile {profileReady ? "✓" : "·"}, risks {riskAssessment ? "✓" : "·"}, finance plan{" "}
                {financialPlan ? "✓" : "·"}.
              </p>
            </div>
            <button
              type="button"
              onClick={() => window.dispatchEvent(new Event("venturemind:open-advisor-chat"))}
              className="inline-flex shrink-0 items-center justify-center rounded-lg bg-white px-4 py-2 text-sm font-bold text-brand-700 hover:bg-brand-50"
            >
              Open AI Advisor chat →
            </button>
          </div>
        </section>
        <div className="grid items-start gap-6 md:grid-cols-2 [&>section.bg-brand-600]:hidden [&>section.bg-slate-950]:hidden md:[&>section:nth-of-type(n+4)]:col-span-2">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900">
            <p className="text-sm font-bold uppercase tracking-widest text-brand-600">Business snapshot</p>
            <h2 className="mt-3 text-xl font-bold">{profile.businessName || "Your startup profile"}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{summary}</p>
            <dl className="mt-5 grid gap-3 text-sm">
              <div>
                <dt className="text-slate-500">Target customers</dt>
                <dd className="font-semibold">{profile.customers || "Not added yet"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Launch timeline</dt>
                <dd className="font-semibold">{profile.timeline || "Not added yet"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Budget gap</dt>
                <dd className="font-semibold">Use Investment Planner next</dd>
              </div>
            </dl>
          </section>
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900">
            <p className="text-sm font-bold uppercase tracking-widest text-brand-600">Local market research</p>
            <h2 className="mt-2 text-xl font-bold">Research nearby business alternatives</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
              Use this search to review real nearby businesses, their offers, customer ratings, and possible market
              gaps. VentureMind never invents competitor names or ratings.
            </p>
            <p className="mt-4 rounded-lg bg-slate-50 p-3 text-sm font-medium dark:bg-slate-800">
              Search: {competitorSearch}
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <a
                href={competitorSearchUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700"
              >
                Search Google Maps ↗
              </a>
              <Button variant="secondary" disabled={competitorLoading} onClick={() => void searchCompetitors()}>
                {competitorLoading ? "Checking listings…" : "View listings here"}
              </Button>
            </div>
            {competitorError && (
              <p className="mt-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-900" role="status">
                {competitorError}
              </p>
            )}
            {competitorResult?.notice && (
              <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{competitorResult.notice}</p>
            )}
            {competitorResult?.competitors.length ? (
              <div className="mt-5 space-y-3">
                {(showAllCompetitors ? competitorResult.competitors : competitorResult.competitors.slice(0, 3)).map((competitor) => (
                  <article
                    key={competitor.place_id}
                    className="rounded-xl border border-slate-200 p-4 dark:border-slate-800"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="font-bold">{competitor.name}</h3>
                        <p className="mt-1 text-xs text-slate-500">{competitor.primary_type ?? "Business listing"}</p>
                      </div>
                      {competitor.rating !== null && (
                        <span className="rounded-full bg-amber-50 px-2 py-1 text-xs font-bold text-amber-800 dark:bg-amber-500/10 dark:text-amber-200">
                          ★ {competitor.rating.toFixed(1)}
                        </span>
                      )}
                    </div>
                    {competitor.address && (
                      <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{competitor.address}</p>
                    )}
                    <p className="mt-2 text-xs text-slate-500">
                      {competitor.user_rating_count !== null
                        ? `${competitor.user_rating_count} Google ratings`
                        : "Rating count unavailable"}
                      {competitor.price_level ? ` · ${competitor.price_level.replaceAll("_", " ")}` : ""}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-3 text-sm font-semibold text-brand-700 dark:text-brand-300">
                      {competitor.maps_url && (
                        <a href={competitor.maps_url} target="_blank" rel="noreferrer">
                          View on Maps ↗
                        </a>
                      )}
                      {competitor.website_url && (
                        <a href={competitor.website_url} target="_blank" rel="noreferrer">
                          Website ↗
                        </a>
                      )}
                    </div>
                  </article>
                ))}
                {competitorResult.competitors.length > 3 && (
                  <button
                    type="button"
                    onClick={() => setShowAllCompetitors((current) => !current)}
                    className="text-sm font-bold text-brand-700 hover:underline dark:text-brand-300"
                  >
                    {showAllCompetitors ? "Show fewer listings" : `Show ${competitorResult.competitors.length - 3} more listings`}
                  </button>
                )}
              </div>
            ) : null}
            <p className="mt-4 text-xs leading-5 text-slate-500">
              Google Maps opens a real-time search using the business category and location in your saved profile.
            </p>
          </section>
          <section className="rounded-2xl bg-brand-600 p-6 text-white">
            <div className="flex items-end justify-between">
              <div>
                <p className="text-sm font-bold uppercase tracking-widest text-brand-100">Lifecycle progress</p>
                <p className="mt-2 text-4xl font-bold">{percent}%</p>
              </div>
              <p className="text-sm text-brand-100">
                {completed}/{milestones.length} milestones
              </p>
            </div>
            <div className="mt-5 h-2 overflow-hidden rounded-full bg-white/20">
              <div className="h-full rounded-full bg-white" style={{ width: `${percent}%` }} />
            </div>
            <div className="mt-6 space-y-2">
              {milestones.map(([, milestone], index) => (
                <label
                  key={milestone}
                  className="flex cursor-pointer items-center gap-3 rounded-lg bg-white/10 px-3 py-2 text-sm"
                >
                  <input
                    type="checkbox"
                    checked={progress[index]}
                    onChange={() => void toggle(index)}
                    className="h-4 w-4 accent-brand-600"
                  />
                  <span className={progress[index] ? "text-brand-100 line-through" : ""}>{milestone}</span>
                </label>
              ))}
            </div>
          </section>
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900">
            <p className="text-sm font-bold uppercase tracking-widest text-brand-600">
              Step 2 · AI startup risk analysis
            </p>
            <h2 className="mt-2 text-xl font-bold">Evidence-based risk assessment</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
              Scores use your saved profile evidence and published rules. They are decision support, not a guarantee of
              business success.
            </p>
            {!profileReady && (
              <p className="mt-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/30 dark:text-amber-100">
                Complete Step 1 first so the analysis has enough business information.
              </p>
            )}
            <Button className="mt-4" disabled={riskLoading || !profileReady} onClick={() => void analyseRisk()}>
              {riskLoading ? "Analysing…" : "Run risk analysis"}
            </Button>
            {riskError && (
              <p className="mt-3 text-sm text-rose-600" role="alert">
                {riskError}
              </p>
            )}
            {riskAssessment && (
              <div className="mt-5">
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="rounded-lg bg-slate-50 p-2 dark:bg-slate-800">
                    <p className="text-xs text-slate-500">Success</p>
                    <strong className="text-lg text-brand-600">{riskAssessment.overall_success_score}</strong>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-2 dark:bg-slate-800">
                    <p className="text-xs text-slate-500">Confidence</p>
                    <strong className="text-lg text-brand-600">{riskAssessment.business_confidence_score}</strong>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-2 dark:bg-slate-800">
                    <p className="text-xs text-slate-500">Risk</p>
                    <strong className="text-lg capitalize text-rose-600">{riskAssessment.risk_level}</strong>
                  </div>
                </div>
                {riskAssessment.ai_explanation && (
                  <article className="mt-4 rounded-xl border border-violet-200 bg-violet-50 p-4 text-sm leading-6 text-violet-950">
                    <p className="text-xs font-bold uppercase tracking-wider text-violet-700">
                      {riskAssessment.ai_explanation.mode === "ollama"
                        ? "Local AI explanation · Ollama"
                        : "Structured explanation"}
                    </p>
                    <p className="mt-2 font-semibold">{riskAssessment.ai_explanation.summary}</p>
                    <button
                      type="button"
                      className="mt-3 text-sm font-bold text-violet-800 underline underline-offset-4"
                      onClick={() => setRiskDetailsOpen((open) => !open)}
                    >
                      {riskDetailsOpen ? "Hide detailed explanation" : "Show detailed explanation"}
                    </button>
                    {riskDetailsOpen && (
                      <div className="mt-3 border-t border-violet-200 pt-3">
                        <p>
                          <strong>Priority gap:</strong> {riskAssessment.ai_explanation.priority_gap}
                        </p>
                        {riskAssessment.ai_explanation.next_actions?.length ? (
                          <ol className="mt-2 list-decimal space-y-1 pl-5">
                            {riskAssessment.ai_explanation.next_actions.map((action) => (
                              <li key={action}>{action}</li>
                            ))}
                          </ol>
                        ) : null}
                      </div>
                    )}
                  </article>
                )}
                <details className="mt-4 rounded-xl border border-slate-200 p-4 dark:border-slate-800">
                  <summary className="cursor-pointer text-sm font-bold">View detailed risk scorecards</summary>
                  <div className="mt-4 space-y-3">
                    {riskAssessment.scorecards.map((score) => (
                      <article key={score.key} className="rounded-lg border border-slate-200 p-3 dark:border-slate-800">
                        <div className="flex justify-between gap-3">
                          <strong className="text-sm">{score.label}</strong>
                          <span className="text-sm font-bold text-rose-600">{score.risk_score}/100</span>
                        </div>
                        <p className="mt-2 text-xs text-slate-500">{score.reasoning}</p>
                        <p className="mt-2 text-xs font-medium text-emerald-700">
                          {score.positive_factors[0] ?? "No supporting evidence yet."}
                        </p>
                        <p className="mt-1 text-xs font-medium text-amber-700">Next: {score.suggestions[0]}</p>
                      </article>
                    ))}
                  </div>
                </details>
              </div>
            )}
          </section>
          <section
            id="financial-plan"
            className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900"
          >
            <p className="text-sm font-bold uppercase tracking-widest text-brand-600">Step 3 · Investment planner</p>
            <h2 className="mt-2 text-xl font-bold">Cash flow and break-even forecast</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
              Enter realistic assumptions in LKR. VentureMind shows a transparent forecast—it is not financial advice or
              a guarantee.
            </p>
            {!riskAssessment && (
              <p className="mt-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/30 dark:text-amber-100">
                Step 2 is required first. Run the risk analysis before creating a financial plan.
              </p>
            )}
            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <fieldset className="rounded-xl border border-slate-200 p-4 dark:border-slate-800">
                <legend className="px-1 text-sm font-bold">Monthly operating costs</legend>
                <div className="mt-2 grid gap-3 sm:grid-cols-2">
                  {(
                    [
                      ["rent", "Rent"],
                      ["utilities", "Utilities and insurance"],
                      ["salaries", "Salaries and contractors"],
                      ["marketing", "Marketing"],
                      ["softwareDelivery", "Software, delivery, tools"],
                      ["loan", "Loan repayment"],
                      ["other", "Other monthly costs"],
                    ] as const
                  ).map(([key, label]) => (
                    <label key={key} className="text-xs font-semibold">
                      {label}
                      <input
                        disabled={!riskAssessment}
                        min="0"
                        type="number"
                        inputMode="decimal"
                        value={financialInputs[key]}
                        onChange={(event) =>
                          setFinancialInputs((current) => ({ ...current, [key]: event.target.value }))
                        }
                        className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent p-2 text-sm font-normal disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700"
                        placeholder="0"
                      />
                    </label>
                  ))}
                </div>
              </fieldset>
              <fieldset className="rounded-xl border border-slate-200 p-4 dark:border-slate-800">
                <legend className="px-1 text-sm font-bold">Startup cash and revenue</legend>
                <div className="mt-2 grid gap-3 sm:grid-cols-2">
                  {(
                    [
                      ["setup", "One-time setup cost"],
                      ["emergency", "Emergency fund"],
                      ["sales", "Expected sales each month"],
                      ["averageSale", "Average sale value"],
                      ["revenue", "Direct monthly revenue estimate"],
                      ["margin", "Gross margin %"],
                    ] as const
                  ).map(([key, label]) => (
                    <label key={key} className="text-xs font-semibold">
                      {label}
                      <input
                        disabled={!riskAssessment}
                        min="0"
                        max={key === "margin" ? 99 : undefined}
                        type="number"
                        inputMode="decimal"
                        value={financialInputs[key]}
                        onChange={(event) =>
                          setFinancialInputs((current) => ({ ...current, [key]: event.target.value }))
                        }
                        className="mt-1 w-full rounded-lg border border-slate-300 bg-transparent p-2 text-sm font-normal disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700"
                        placeholder={key === "margin" ? "50" : "0"}
                      />
                    </label>
                  ))}
                </div>
                <p className="mt-3 text-xs leading-5 text-slate-500">
                  Use either a direct monthly revenue estimate, or both monthly sales and average sale value.
                </p>
              </fieldset>
            </div>
            <Button
              className="mt-5"
              disabled={financialLoading || !riskAssessment}
              onClick={() => void makeFinancialPlan()}
            >
              {financialLoading ? "Calculating…" : "Generate financial plan"}
            </Button>
            {financialError && (
              <p className="mt-3 rounded-lg bg-rose-50 p-3 text-sm text-rose-700" role="alert">
                {financialError}
              </p>
            )}
            {financialPlan && (
              <div className="mt-5">
                <p className="text-sm font-bold text-emerald-700">
                  Forecast result · {String(financialPlan.results.status).replace("-", " ")}
                </p>
                <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
                  {[
                    ["Monthly revenue", "monthly_revenue", true],
                    ["Monthly expenses", "monthly_expenses", true],
                    ["Estimated monthly result", "monthly_profit", true],
                    ["Break-even revenue", "break_even_revenue", true],
                    ["Break-even sales", "break_even_units", false],
                    ["Cash runway", "runway_months", false],
                    ["Upfront cash needed", "upfront_cash_needed", true],
                    ["Funding gap", "cash_gap", true],
                    ["Annual ROI", "annual_roi_percent", false],
                  ].map(([label, key, currency]) => (
                    <div key={String(key)} className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800">
                      <p className="text-xs text-slate-500">{label}</p>
                      <strong>
                        {currency
                          ? formatLkr(financialPlan.results[String(key)])
                          : (financialPlan.results[String(key)] ?? "Not reached")}
                        {key === "runway_months" && financialPlan.results[String(key)] !== null ? " months" : ""}
                        {key === "annual_roi_percent" && financialPlan.results[String(key)] !== null ? "%" : ""}
                      </strong>
                    </div>
                  ))}
                </div>
                <p className="mt-3 rounded-lg bg-brand-50 p-3 text-xs leading-5 text-brand-900 dark:bg-brand-500/10 dark:text-brand-100">
                  {String(financialPlan.results.methodology)}
                </p>
              </div>
            )}
          </section>
          {profile.country === "Sri Lanka" && (
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card dark:border-slate-800 dark:bg-slate-900">
              <p className="text-sm font-bold uppercase tracking-widest text-brand-600">Sri Lanka registration guide</p>
              <h2 className="mt-2 text-xl font-bold">Register your business step by step</h2>
              <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
                Follow these steps in order. Open a card for the documents and official online guide. Requirements can
                differ by business structure, district, and industry.
              </p>
              <div className="mt-5 space-y-3">
                <details className="rounded-xl border border-slate-200 p-4 dark:border-slate-700" open>
                  <summary className="cursor-pointer font-bold">1. Choose a business structure and reserve a name</summary>
                  <div className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                    <p>Decide whether you will operate as a sole proprietor, partnership, or company. Check that the proposed name is available before preparing incorporation documents.</p>
                    <p><strong>Prepare:</strong> proposed company name, owner/director details, registered address, business activity, and contact details.</p>
                    <a className="inline-block font-semibold text-brand-700 dark:text-brand-300" href="https://drc.gov.lk/en/" target="_blank" rel="noreferrer">Open Department of Registrar of Companies ↗</a>
                  </div>
                </details>
                <details className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                  <summary className="cursor-pointer font-bold">2. Submit company incorporation through eROC</summary>
                  <div className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                    <p>Create or use an eROC account, complete the system-generated incorporation forms, review the details, submit them, and keep your receipt/reference number.</p>
                    <p><strong>Tip:</strong> use system-generated forms where the official portal requires them.</p>
                    <a className="inline-block font-semibold text-brand-700 dark:text-brand-300" href="https://erocapiv2.drc.gov.lk/pdf/3.6.1%28a%29Incorporation_Frontend.pdf" target="_blank" rel="noreferrer">Open eROC new-user guide ↗</a>
                  </div>
                </details>
                <details className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                  <summary className="cursor-pointer font-bold">3. Complete beneficial ownership details where applicable</summary>
                  <div className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                    <p>After incorporation and payment, follow the official beneficial-ownership process if it applies to your company. Keep identification and ownership information accurate.</p>
                    <a className="inline-block font-semibold text-brand-700 dark:text-brand-300" href="https://drc.gov.lk/en/?page_id=4709" target="_blank" rel="noreferrer">Watch official DRC registration video guides ↗</a>
                  </div>
                </details>
                <details className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                  <summary className="cursor-pointer font-bold">4. Obtain a TIN and check local licences</summary>
                  <div className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                    <p>Register with the Inland Revenue Department to obtain a TIN, then check trade, health, building, food, tourism, or sector licences with the relevant local authority.</p>
                    <a className="inline-block font-semibold text-brand-700 dark:text-brand-300" href="https://www.ird.gov.lk/en/eservices/sitepages/registration.aspx?menuid=1801" target="_blank" rel="noreferrer">Open official IRD TIN registration guide ↗</a>
                    <a className="ml-4 inline-block font-semibold text-brand-700 dark:text-brand-300" href="https://www.ird.gov.lk/en/eservices/sitepages/e-learning.aspx?menuid=180201" target="_blank" rel="noreferrer">Open IRD e-learning videos ↗</a>
                  </div>
                </details>
              </div>
            </section>
          )}
          <section className="rounded-2xl bg-slate-950 p-6 text-white">
            <p className="text-sm font-bold uppercase tracking-widest text-accent-300">AI business advisor</p>
            <h2 className="mt-2 text-xl font-bold">Ask about your startup plan</h2>
            <p className="mt-2 text-sm text-slate-300">
              Uses your saved context when available. If the AI service is unavailable, VentureMind provides a
              transparent structured planning response.
            </p>
            <textarea
              value={advisorQuestion}
              onChange={(event) => setAdvisorQuestion(event.target.value)}
              rows={3}
              className="mt-4 w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm"
            />
            <Button
              className="mt-3"
              disabled={advisorLoading || !advisorQuestion.trim()}
              onClick={() => void askAdvisor()}
            >
              {advisorLoading ? "Thinking…" : "Ask advisor"}
            </Button>
            {!backendEnabled && (
              <p className="mt-3 text-xs text-slate-300">
                A structured planning response is available without a saved cloud profile.
              </p>
            )}
            {advisorReply && (
              <div className="mt-4 rounded-xl bg-white/10 p-4 text-sm leading-6">
                <p className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-300">
                  {advisorReply.mode === "gemini" ? "Gemini guidance" : "Structured guidance"}
                </p>
                {advisorReply.response}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
