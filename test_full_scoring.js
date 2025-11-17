const fs = require('fs');
const path = require('path');

// Load data
const enrichmentPath = path.join(__dirname, 'public', 'use_cases_enrichment.json');
const enrichmentData = JSON.parse(fs.readFileSync(enrichmentPath, 'utf-8'));

const toolsPath = path.join(__dirname, 'public', 'ai_tracker_enhanced.json');
const toolsData = JSON.parse(fs.readFileSync(toolsPath, 'utf-8'));

// Simulated search criteria from smart-search API
const searchCriteria = {
  useCases: ['website-creation', 'api-creation', 'database-work'],
  excludeTools: [],
  requiredFeatures: [],
  constraints: {
    codingLevel: 'developer',
    budget: null,
    experienceLevel: 'intermediate'
  }
};

console.log('TEST: Full-stack web application search');
console.log('='.repeat(60));
console.log('Search criteria:', JSON.stringify(searchCriteria, null, 2));
console.log('');

// Test with Cursor
const toolName = 'Cursor';
const enrichment = enrichmentData[toolName];

if (!enrichment) {
  console.log(`❌ ${toolName} not found in enrichment data`);
  process.exit(1);
}

console.log(`\nTesting: ${toolName}`);
console.log('-'.repeat(60));

const useCases = enrichment.use_case_compatibility || {};
console.log('Available use cases:', Object.keys(useCases).join(', '));
console.log('');

let score = 0;
let useCaseScore = 0;
let totalWeight = 0;

console.log('USE CASE SCORING:');
for (const reqUseCase of searchCriteria.useCases) {
  const compatibility = useCases[reqUseCase];
  if (compatibility) {
    const weight = compatibility.type === 'primary' ? 1.0 : 0.5;
    const strength = compatibility.strength;

    console.log(`  ${reqUseCase}:`);
    console.log(`    - strength: ${strength}`);
    console.log(`    - type: ${compatibility.type}`);
    console.log(`    - weight: ${weight}`);
    console.log(`    - contribution: ${strength} * ${weight} = ${strength * weight}`);

    useCaseScore += strength * weight;
    totalWeight += weight;
  } else {
    console.log(`  ${reqUseCase}: NOT FOUND`);
  }
}

console.log('');
console.log(`Total useCaseScore: ${useCaseScore}`);
console.log(`Total weight: ${totalWeight}`);

if (totalWeight > 0) {
  const avgStrength = useCaseScore / totalWeight;
  console.log(`Average strength: ${avgStrength}`);

  const normalized = avgStrength / 100;
  console.log(`Normalized (÷100): ${normalized}`);

  const useCasePoints = normalized * 60;
  console.log(`Use case points (×60): ${useCasePoints}`);

  score += useCasePoints;
}

// Add other scoring components
const technicalProfile = enrichment.technical_profile || {};
const codingLevel = technicalProfile.coding_level;

console.log('');
console.log('TECHNICAL LEVEL SCORING:');
console.log(`  Tool coding level: ${codingLevel}`);
console.log(`  Required: ${searchCriteria.constraints.codingLevel}`);

if (searchCriteria.constraints.codingLevel) {
  const levelMatch = codingLevel === searchCriteria.constraints.codingLevel;
  const levelScore = levelMatch ? 20 : 10;
  console.log(`  Match: ${levelMatch ? 'YES' : 'NO'}`);
  console.log(`  Points: ${levelScore}`);
  score += levelScore;
} else {
  console.log(`  No constraint - default points: 20`);
  score += 20;
}

// Budget scoring (10 points)
console.log('');
console.log('BUDGET SCORING:');
console.log(`  No budget constraint - default points: 10`);
score += 10;

// Experience level scoring (10 points)
console.log('');
console.log('EXPERIENCE LEVEL SCORING:');
console.log(`  No experience constraint - default points: 10`);
score += 10;

console.log('');
console.log('='.repeat(60));
console.log(`FINAL SCORE: ${score.toFixed(1)}%`);
console.log('='.repeat(60));
