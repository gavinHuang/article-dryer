const OpenAI = require('openai');

const openai = new OpenAI({
  // baseURL: 'https://api.deepseek.com',
  apiKey: process.env.DEEPSEEK_API_KEY,
});

const processText = async (text, res) => {
  try {
    // print text:
    console.log(">>>>input:" + text);
    const completion = await openai.chat.completions.create({
      messages: [
        {
          role: "system",
          content: `Understand the meaning of this paragraph, rewrite it into a shorter version with keywords. 
          Return with markdown format like this:

          # Shortened
          Shortened text...
          # Keywords
          - keyword1
          - keyword2
          
          # Shortened
          Shortened text...
          # Keywords
          - keyword1
          - keyword2
          
          Below is the article:`,
        },
        { role: "user", content: text },
      ],
      model: "gpt-4o-mini",
      stream: true,
    }
  );

    // Set headers for streaming response
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    for await (const chunk of completion) {
      const content = chunk.choices[0]?.delta?.content || '';
      res.write(`${JSON.stringify({ content })}\n\n`);
      process.stdout.write(content);
    }
    res.end();

    // // Extract the response content
    // const responseContent = completion.choices[0].message.content;

    // // Debug: Log the raw response
    // console.log('Raw Response:', responseContent);

    // // Strip out Markdown code blocks (```json and ```)
    // const jsonString = responseContent.replace(/```json|```/g, '').trim();

    // // Parse the JSON string
    // const jsonObject = JSON.parse(jsonString);

    // // Validate the response structure
    // if (!jsonObject.processedContent) {
    //   throw new Error('Invalid response structure: processedContent missing');
    // }

    // // Return the processed content
    // return jsonObject.processedContent;
  } catch (error) {
    console.error('Error calling DeepSeek-V3 API:', error.message);
    throw new Error('Failed to process text using DeepSeek-V3');
  }
};

module.exports = { processText };