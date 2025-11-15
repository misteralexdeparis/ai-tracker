/**
 * Use Case Matcher - Client-side matching algorithm
 * Zero API cost - runs 100% in browser
 */

export interface UseCaseCompatibility {
  [useCaseId: string]: {
    strength: number;
    type: 'primary' | 'secondary';
    notes: string;
    limitations?: string[];
  };
}

export interface ToolEnrichment {
  use_case_compatibility: UseCaseCompatibility;
  technical_profile: {
    coding_level: 'no-code' | 'low-code' | 'developer' | 'expert';
    user_levels: string[];
    platform: string;
    integrations?: string[];
    learning_curve: 'easy' | 'moderate' | 'steep';
  };
  best_for: {
    primary: string;
    ideal_user: string;
    key_differentiator: string;
  };
  limitations: string[];
  pricing_tier: {
    has_free_tier: boolean;
    free_tier_limits?: string;
    recommended_tier: string;
    enterprise_available: boolean;
  };
  enrichment_meta: {
    source: string;
    model?: string;
    date: string;
    version: string;
    manually_reviewed: boolean;
  };
}

export interface Tool {
  name: string;
  category: string;
  description: string;
  final_score: number;
  gartner_quadrant?: string;
  url?: string;
  pricing?: string;
  [key: string]: any;
}

export interface UserRequirements {
  text_input: string;
  use_cases: string[]; // Detected use case IDs
  coding_level?: 'no-code' | 'low-code' | 'developer' | 'expert';
  budget?: 'free' | 'paid' | 'any';
  platform?: string;
  experience_level?: 'beginner' | 'intermediate' | 'expert';
}

export interface ToolMatch {
  tool: Tool;
  enrichment: ToolEnrichment;
  compatibilityScore: number; // 0-100
  overallScore: number; // Gartner score
  matchedUseCases: {
    id: string;
    name: string;
    strength: number;
    type: 'primary' | 'secondary';
  }[];
  reasoning: string[];
  limitations: string[];
  confidence: number; // 0-100 - how confident we are in the match
}

/**
 * Keyword mapping for intelligent text parsing
 * Maps common words/phrases to use case IDs
 */
const KEYWORD_MAP: Record<string, string[]> = {
  // Presentations
  'presentation': ['business-presentation-creation', 'pitch-deck-creation'],
  'powerpoint': ['business-presentation-creation', 'data-presentation'],
  'slides': ['business-presentation-creation', 'marketing-presentation'],
  'pitch deck': ['pitch-deck-creation'],
  'deck': ['pitch-deck-creation', 'business-presentation-creation'],

  // Development
  'code': ['full-stack-web-development', 'code-generation', 'frontend-development'],
  'coding': ['full-stack-web-development', 'code-generation'],
  'developer': ['full-stack-web-development', 'code-generation'],
  'programming': ['full-stack-web-development', 'backend-development'],
  'app': ['full-stack-web-development', 'mobile-app-development'],
  'website': ['full-stack-web-development', 'frontend-development'],
  'web app': ['full-stack-web-development'],
  'frontend': ['frontend-development'],
  'backend': ['backend-development'],
  'full stack': ['full-stack-web-development'],
  'mobile': ['mobile-app-development'],
  'react': ['frontend-development'],
  'vue': ['frontend-development'],
  'angular': ['frontend-development'],
  'api': ['backend-development'],
  'database': ['database-design', 'backend-development'],
  'sql': ['database-design', 'sql-query-generation'],
  'debug': ['debugging'],
  'refactor': ['code-refactoring'],
  'test': ['test-writing'],

  // Content Creation
  'blog': ['blog-post-writing', 'seo-content-writing'],
  'article': ['blog-post-writing', 'long-form-writing'],
  'content': ['marketing-copy', 'blog-post-writing'],
  'marketing': ['marketing-copy', 'social-media-content'],
  'copy': ['marketing-copy', 'copywriting'],
  'email': ['email-drafting', 'marketing-copy'],
  'social media': ['social-media-content'],
  'linkedin': ['social-media-content'],
  'twitter': ['social-media-content'],
  'seo': ['seo-content-writing'],
  'writing': ['long-form-writing', 'blog-post-writing'],

  // Research & Analysis
  'research': ['academic-research', 'web-research', 'market-research'],
  'analyze': ['multi-document-analysis', 'data-analysis'],
  'analysis': ['multi-document-analysis', 'competitive-analysis'],
  'document': ['multi-document-analysis', 'pdf-analysis'],
  'pdf': ['pdf-analysis', 'multi-document-analysis'],
  'papers': ['academic-research', 'multi-document-analysis'],
  'study': ['academic-research'],
  'summarize': ['summarization', 'meeting-summarization'],
  'summary': ['summarization'],
  'market': ['market-research', 'competitive-analysis'],
  'competitor': ['competitive-analysis'],

  // Visual & Media
  'image': ['image-generation', 'image-editing'],
  'picture': ['image-generation'],
  'photo': ['image-editing', 'image-generation'],
  'logo': ['logo-design'],
  'design': ['ui-design', 'logo-design', 'mockup-creation'],
  'video': ['video-generation', 'video-editing'],
  'animation': ['video-generation'],
  'ui': ['ui-design', 'mockup-creation'],
  'mockup': ['mockup-creation'],
  'diagram': ['diagram-creation'],
  'flowchart': ['diagram-creation'],
  'audio': ['audio-generation', 'voice-cloning'],
  'voice': ['voice-cloning', 'audio-generation'],
  'podcast': ['podcast-generation'],

  // Productivity
  'meeting': ['meeting-transcription', 'meeting-summarization'],
  'notes': ['note-taking', 'meeting-summarization'],
  'transcribe': ['meeting-transcription'],
  'task': ['workflow-automation'],
  'automate': ['workflow-automation', 'automation-scripts'],
  'workflow': ['workflow-automation'],

  // Data
  'data': ['data-analysis', 'data-visualization'],
  'analytics': ['data-analysis', 'reporting'],
  'dashboard': ['data-visualization', 'reporting'],
  'chart': ['data-visualization'],
  'graph': ['data-visualization'],
  'spreadsheet': ['spreadsheet-automation'],
  'excel': ['spreadsheet-automation'],

  // Communication
  'chatbot': ['chatbot-creation', 'customer-support'],
  'support': ['customer-support'],
  'translate': ['translation'],
  'translation': ['translation'],
  'grammar': ['grammar-checking', 'proofreading'],
  'proofread': ['proofreading'],

  // Business
  'business plan': ['business-plan-writing'],
  'swot': ['swot-analysis'],
  'proposal': ['proposal-writing'],
};

/**
 * Extract use cases from user text input
 */
export function parseUserInput(text: string): string[] {
  const lowercaseText = text.toLowerCase();
  const detectedUseCases = new Set<string>();

  // Check for keyword matches
  for (const [keyword, useCases] of Object.entries(KEYWORD_MAP)) {
    if (lowercaseText.includes(keyword)) {
      useCases.forEach(uc => detectedUseCases.add(uc));
    }
  }

  return Array.from(detectedUseCases);
}

/**
 * Calculate compatibility score between user requirements and a tool
 * Returns 0-100 score
 */
export function calculateCompatibilityScore(
  userReqs: UserRequirements,
  tool: Tool,
  enrichment: ToolEnrichment
): { score: number; matchedUseCases: any[]; confidence: number } {
  let score = 0;
  const maxScore = 100;
  const matchedUseCases: any[] = [];

  // 1. Use case matching (60% of score)
  if (userReqs.use_cases.length > 0) {
    let useCaseScore = 0;
    let totalWeight = 0;

    for (const reqUseCase of userReqs.use_cases) {
      const compatibility = enrichment.use_case_compatibility[reqUseCase];
      if (compatibility) {
        const weight = compatibility.type === 'primary' ? 1.0 : 0.5;
        useCaseScore += compatibility.strength * weight;
        totalWeight += weight;

        matchedUseCases.push({
          id: reqUseCase,
          name: reqUseCase.replace(/-/g, ' '),
          strength: compatibility.strength,
          type: compatibility.type,
        });
      }
    }

    if (totalWeight > 0) {
      score += (useCaseScore / totalWeight) * 60; // 60% of total score
    }
  }

  // 2. Technical level match (20% of score)
  if (userReqs.coding_level) {
    const toolLevel = enrichment.technical_profile.coding_level;
    if (userReqs.coding_level === toolLevel) {
      score += 20;
    } else {
      // Partial match for adjacent levels
      const levels = ['no-code', 'low-code', 'developer', 'expert'];
      const userIdx = levels.indexOf(userReqs.coding_level);
      const toolIdx = levels.indexOf(toolLevel);
      const distance = Math.abs(userIdx - toolIdx);
      score += Math.max(0, 20 - (distance * 7)); // Penalize distance
    }
  } else {
    score += 20; // No preference = full score
  }

  // 3. Budget match (10% of score)
  if (userReqs.budget) {
    if (userReqs.budget === 'free' && enrichment.pricing_tier.has_free_tier) {
      score += 10;
    } else if (userReqs.budget === 'paid' || userReqs.budget === 'any') {
      score += 10;
    } else if (userReqs.budget === 'free' && !enrichment.pricing_tier.has_free_tier) {
      score += 0; // No free tier = 0 points
    }
  } else {
    score += 10; // No preference
  }

  // 4. Experience level match (10% of score)
  if (userReqs.experience_level) {
    if (enrichment.technical_profile.user_levels.includes(userReqs.experience_level)) {
      score += 10;
    } else {
      score += 5; // Partial credit
    }
  } else {
    score += 10;
  }

  // Calculate confidence (how sure we are this is a good match)
  const confidence = Math.min(100, (matchedUseCases.length * 30) + (userReqs.use_cases.length > 0 ? 40 : 20));

  return {
    score: Math.min(score, maxScore),
    matchedUseCases,
    confidence,
  };
}

/**
 * Generate human-readable reasoning for why a tool matches
 */
function generateReasoning(
  userReqs: UserRequirements,
  tool: Tool,
  enrichment: ToolEnrichment,
  matchedUseCases: any[]
): string[] {
  const reasons: string[] = [];

  // Primary use case matches
  const primaryMatches = matchedUseCases.filter(m => m.type === 'primary');
  if (primaryMatches.length > 0) {
    const useCaseNames = primaryMatches.map(m => m.name).join(', ');
    reasons.push(`Excellent for: ${useCaseNames}`);
  }

  // Key differentiator
  if (enrichment.best_for.key_differentiator) {
    reasons.push(enrichment.best_for.key_differentiator);
  }

  // Technical match
  if (userReqs.coding_level) {
    const levelMatch = userReqs.coding_level === enrichment.technical_profile.coding_level;
    if (levelMatch) {
      reasons.push(`Perfect match for ${userReqs.coding_level} users`);
    }
  }

  // Budget match
  if (userReqs.budget === 'free' && enrichment.pricing_tier.has_free_tier) {
    reasons.push('Has a free tier available');
  }

  return reasons;
}

/**
 * Main matching function: finds best tools for user requirements
 */
export function matchToolsToUserNeeds(
  userInput: UserRequirements,
  tools: Tool[],
  enrichments: Record<string, ToolEnrichment>
): ToolMatch[] {
  const matches: ToolMatch[] = [];

  for (const tool of tools) {
    const enrichment = enrichments[tool.name];
    if (!enrichment) continue; // Skip tools without enrichment

    const { score, matchedUseCases, confidence } = calculateCompatibilityScore(
      userInput,
      tool,
      enrichment
    );

    // Only include tools with reasonable compatibility (>= 30%)
    if (score >= 30) {
      const reasoning = generateReasoning(userInput, tool, enrichment, matchedUseCases);

      matches.push({
        tool,
        enrichment,
        compatibilityScore: score,
        overallScore: tool.final_score || 0,
        matchedUseCases,
        reasoning,
        limitations: enrichment.limitations,
        confidence,
      });
    }
  }

  // Sort by compatibility score (primary), then overall score (secondary)
  matches.sort((a, b) => {
    if (Math.abs(a.compatibilityScore - b.compatibilityScore) > 5) {
      return b.compatibilityScore - a.compatibilityScore;
    }
    return b.overallScore - a.overallScore;
  });

  // Return top 10
  return matches.slice(0, 10);
}

/**
 * Build user requirements from form inputs
 */
export function buildUserRequirements(
  textInput: string,
  codingLevel?: string,
  budget?: string,
  experienceLevel?: string
): UserRequirements {
  const useCases = parseUserInput(textInput);

  return {
    text_input: textInput,
    use_cases: useCases,
    coding_level: codingLevel as any,
    budget: budget as any,
    experience_level: experienceLevel as any,
  };
}

/**
 * Wrapper function that loads data and matches tools based on a query string
 * This is the function that should be called from React components
 * Returns a simplified format for the results page
 */
export async function matchToolsToQuery(query: string): Promise<Array<{
  tool: Tool;
  matchScore: number;
  matchReasons: string[];
}>> {
  // Load tools data
  const toolsResponse = await fetch('/ai_tracker_enhanced.json');
  const toolsData = await toolsResponse.json();
  const tools: Tool[] = toolsData.tools || [];

  // Load enrichments
  const enrichmentsResponse = await fetch('/use_cases_enrichment.json');
  const enrichments: Record<string, ToolEnrichment> = await enrichmentsResponse.json();

  // Build user requirements from query
  const userRequirements = buildUserRequirements(query);

  // Match tools
  const matches = matchToolsToUserNeeds(userRequirements, tools, enrichments);

  // Transform to simplified format expected by results page
  return matches.map(match => ({
    tool: match.tool,
    matchScore: match.compatibilityScore,
    matchReasons: match.reasoning ? [match.reasoning] : []
  }));
}

/**
 * Smart AI-powered search with automatic fallback to local search
 * Cost: ~$0.005-0.01 per search
 * Falls back to matchToolsToQuery if AI fails
 */
export async function matchToolsToQuerySmart(query: string): Promise<{
  results: Array<{
    tool: Tool;
    matchScore: number;
    matchReasons: string[];
  }>;
  mode: 'ai-powered' | 'fallback';
  aiReasoning?: string;
}> {
  try {
    // Try AI-powered search first
    const response = await fetch('/api/smart-search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error('AI search failed, using fallback');
    }

    // Load tools and enrichments
    const toolsResponse = await fetch('/ai_tracker_enhanced.json');
    const toolsData = await toolsResponse.json();
    const tools: Tool[] = toolsData.tools || [];

    const enrichmentsResponse = await fetch('/use_cases_enrichment.json');
    const enrichments: Record<string, ToolEnrichment> = await enrichmentsResponse.json();

    const { criteria } = data;

    // Apply AI-extracted constraints
    let filteredTools = tools.filter(tool => {
      // Exclude explicitly excluded tools
      if (criteria.excludeTools.includes(tool.name)) {
        return false;
      }

      // Filter by coding level
      const enrichment = enrichments[tool.name];
      if (criteria.constraints.codingLevel && enrichment) {
        const toolCodingLevel = enrichment.technical_profile?.coding_level;

        // If user wants no-code, exclude developer/expert tools
        if (criteria.constraints.codingLevel === 'no-code' &&
            (toolCodingLevel === 'developer' || toolCodingLevel === 'expert')) {
          return false;
        }

        // If user is expert developer, deprioritize no-code tools
        if (criteria.constraints.codingLevel === 'expert' &&
            toolCodingLevel === 'no-code') {
          return false;
        }
      }

      return true;
    });

    // Build smart user requirements
    const userRequirements: UserRequirements = {
      text_input: query,
      use_cases: criteria.useCases.reduce((acc, uc) => {
        acc[uc] = 'high';
        return acc;
      }, {} as Record<string, 'high' | 'medium' | 'low'>),
      coding_level: criteria.constraints.codingLevel as any,
      budget: criteria.constraints.budget as any,
      experience_level: criteria.constraints.experienceLevel as any,
    };

    // IMPORTANT: Filter out tools that have NO matching use cases
    // This prevents irrelevant tools from appearing just because they match coding level
    const useCaseFilteredTools = filteredTools.filter(tool => {
      const enrichment = enrichments[tool.name];
      if (!enrichment || !enrichment.use_case_compatibility) {
        return false; // No enrichment data = exclude
      }

      // Check if tool supports at least ONE of the requested use cases
      const hasMatchingUseCase = criteria.useCases.some(useCase => {
        const compatibility = enrichment.use_case_compatibility[useCase];
        return compatibility && compatibility.strength >= 0.3; // At least 30% compatibility
      });

      return hasMatchingUseCase;
    });

    // Match tools with smart filtering
    const matches = matchToolsToUserNeeds(userRequirements, useCaseFilteredTools, enrichments);

    return {
      results: matches.map(match => ({
        tool: match.tool,
        matchScore: match.compatibilityScore,
        matchReasons: match.reasoning ? [match.reasoning, criteria.reasoning] : [criteria.reasoning]
      })),
      mode: 'ai-powered',
      aiReasoning: criteria.reasoning,
    };

  } catch (error) {
    console.warn('AI search failed, falling back to local search:', error);

    // Fallback to local search
    const results = await matchToolsToQuery(query);
    return {
      results,
      mode: 'fallback',
    };
  }
}
