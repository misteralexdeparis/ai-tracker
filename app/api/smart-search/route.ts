/**
 * Smart AI-powered tool search API
 * Cost: ~$0.005-0.01 per search
 * Falls back to local search if API fails
 */

import { NextRequest, NextResponse } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

interface SearchCriteria {
  useCases: string[];
  excludeTools: string[];
  requiredFeatures: string[];
  constraints: {
    codingLevel?: 'no-code' | 'low-code' | 'developer' | 'expert';
    budget?: 'free' | 'starter' | 'professional' | 'enterprise';
    experienceLevel?: 'beginner' | 'intermediate' | 'advanced';
  };
  reasoning: string;
}

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    // Use Claude to analyze the user's query
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: `Analyze this AI tool search query and extract structured criteria.

User query: "${query}"

Return a JSON object with:
{
  "useCases": ["primary-use-case-1", "use-case-2"],
  "excludeTools": ["tool-to-exclude"],
  "requiredFeatures": ["feature-1", "feature-2"],
  "constraints": {
    "codingLevel": "no-code" | "low-code" | "developer" | "expert" | null,
    "budget": "free" | "starter" | "professional" | "enterprise" | null,
    "experienceLevel": "beginner" | "intermediate" | "advanced" | null
  },
  "reasoning": "Brief explanation of the analysis"
}

Use cases taxonomy (use exact IDs):

Content Creation & Writing:
- business-presentation-creation, pitch-deck-creation, data-presentation, marketing-presentation
- long-form-writing, blog-post-writing, marketing-copy, social-media-content
- technical-documentation, email-drafting, seo-content-writing, copywriting

Code & Development:
- website-creation (any website/web app, no-code to full-stack)
- mobile-app-creation (any mobile app)
- code-assistance (code completion, generation, help)
- code-quality (review, refactoring, optimization)
- bug-fixing (debugging, troubleshooting)
- testing (unit tests, integration tests, e2e)
- task-automation (scripts, workflows)
- api-creation (REST, GraphQL, backend services)
- database-work (SQL, schemas, queries)

Research & Analysis:
- multi-document-analysis, academic-research, market-research, competitive-analysis
- data-synthesis, web-research, pdf-analysis, summarization

Visual & Multimedia:
- image-generation, image-editing, logo-design
- video-generation, video-editing
- ui-design, mockup-creation, diagram-creation
- audio-generation, voice-cloning, podcast-generation

Productivity & Automation:
- meeting-transcription, meeting-summarization, note-taking
- email-management, workflow-automation, document-generation

Data & Analytics:
- data-analysis, data-visualization, spreadsheet-automation
- sql-query-generation, reporting

Communication:
- chatbot-creation, customer-support, translation
- proofreading, grammar-checking

Business & Strategy:
- business-plan-writing, swot-analysis, proposal-writing

Constraints:
- If user mentions "beginner", "no code", "non-technical" → codingLevel: "no-code"
- If user mentions "developer", "coding", "programming" → codingLevel: "developer"
- If user mentions "free", "no budget" → budget: "free"

Exclude tools that clearly don't match (e.g., if "no-code" is required, exclude developer tools like GitHub Copilot).`,
        },
      ],
    });

    const responseText = message.content[0].type === 'text' ? message.content[0].text : '';

    // Extract JSON from response (handle markdown code blocks)
    let jsonText = responseText.trim();
    if (jsonText.startsWith('```json')) {
      jsonText = jsonText.slice(7);
    } else if (jsonText.startsWith('```')) {
      jsonText = jsonText.slice(3);
    }
    if (jsonText.endsWith('```')) {
      jsonText = jsonText.slice(0, -3);
    }

    const criteria: SearchCriteria = JSON.parse(jsonText.trim());

    return NextResponse.json({
      success: true,
      criteria,
      mode: 'ai-powered',
    });

  } catch (error) {
    console.error('Smart search error:', error);

    // Return error to trigger fallback on client
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        mode: 'fallback',
      },
      { status: 500 }
    );
  }
}
