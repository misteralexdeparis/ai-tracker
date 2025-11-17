// Test the smart-search API directly
const fetch = require('node-fetch');

async function testSmartSearch(query) {
  console.log(`Testing query: "${query}"`);
  console.log('='.repeat(60));

  try {
    const response = await fetch('http://localhost:3000/api/smart-search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    const data = await response.json();

    if (data.success) {
      console.log('\n✅ API Success\n');
      console.log('Mode:', data.mode);
      console.log('\nCriteria returned:');
      console.log(JSON.stringify(data.criteria, null, 2));
    } else {
      console.log('\n❌ API Failed\n');
      console.log('Error:', data.error);
    }
  } catch (error) {
    console.log('\n❌ Request Failed\n');
    console.log('Error:', error.message);
  }
}

// Test both queries
(async () => {
  await testSmartSearch('Build a full-stack web application');
  console.log('\n\n');
  await testSmartSearch('je veux faire des video par ia');
})();
