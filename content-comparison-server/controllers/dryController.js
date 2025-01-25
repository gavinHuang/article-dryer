const OpenAI = require('openai');

const openai = new OpenAI({
  baseURL: 'https://api.deepseek.com',
  apiKey: process.env.DEEPSEEK_API_KEY,
});

const processText = async (text) => {
  try {
    const completion = await openai.chat.completions.create({
      messages: [
        {
          role: "system",
          content: `You will be given an article, process the content to get shorter version.
          Process it paragraph by paragraph, skip words and sentences that are non-essential to the structure and flow of meaning. 

          Return with JSON format like this:
          {
            processedContent: [
              {
                original: "Original text...",
                shortened: "Shortened text...",
                keywords: ["keyword1", "keyword2"]
              }
            ]
          }
          Below is the article:`,
        },
        { role: "user", content: text },
      ],
      model: "deepseek-chat",
    });

    // Extract the response content
    const responseContent = completion.choices[0].message.content;

    // Debug: Log the raw response
    console.log('Raw Response:', responseContent);

    // Strip out Markdown code blocks (```json and ```)
    const jsonString = responseContent.replace(/```json|```/g, '').trim();

    // Parse the JSON string
    const jsonObject = JSON.parse(jsonString);

    // Validate the response structure
    if (!jsonObject.processedContent) {
      throw new Error('Invalid response structure: processedContent missing');
    }

    // Return the processed content
    return jsonObject.processedContent;
  } catch (error) {
    console.error('Error calling DeepSeek-V3 API:', error.message);
    throw new Error('Failed to process text using DeepSeek-V3');
  }
};

module.exports = { processText };