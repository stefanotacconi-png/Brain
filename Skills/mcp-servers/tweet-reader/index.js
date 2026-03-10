#!/usr/bin/env node
import { ProxyAgent, fetch } from "undici";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Respect system proxy (required in Claude Code sandbox)
const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;
const dispatcher = proxyUrl ? new ProxyAgent(proxyUrl) : undefined;

const server = new Server(
  { name: "tweet-reader", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

function extractTweetId(input) {
  // Match standard URLs: twitter.com/user/status/ID or x.com/user/status/ID
  const urlMatch = input.match(
    /(?:twitter\.com|x\.com)\/(?:#!\/)?(?:\w+)\/status(?:es)?\/(\d+)/i
  );
  if (urlMatch) return urlMatch[1];

  // Match short-form URLs: x.com/i/status/ID
  const shortMatch = input.match(/(?:twitter\.com|x\.com)\/i\/status\/(\d+)/i);
  if (shortMatch) return shortMatch[1];

  // Match bare numeric ID
  const idMatch = input.match(/^(\d{10,})$/);
  if (idMatch) return idMatch[1];

  return null;
}

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "read_tweet",
      description:
        "Read the content of a tweet or X post. Provide a twitter.com or x.com URL, or a tweet ID.",
      inputSchema: {
        type: "object",
        properties: {
          url: {
            type: "string",
            description: "Twitter/X URL (e.g. https://x.com/user/status/123) or bare tweet ID",
          },
        },
        required: ["url"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "read_tweet") {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  const { url } = request.params.arguments;
  const tweetId = extractTweetId(url);

  if (!tweetId) {
    return {
      content: [
        {
          type: "text",
          text: `Could not extract a tweet ID from: "${url}". Please provide a full twitter.com or x.com URL.`,
        },
      ],
    };
  }

  try {
    const res = await fetch(`https://api.vxtwitter.com/Twitter/status/${tweetId}`, {
      headers: { "User-Agent": "tweet-reader-mcp/1.0" },
      ...(dispatcher ? { dispatcher } : {}),
      signal: AbortSignal.timeout(15000),
    });

    if (!res.ok) {
      throw new Error(`vxtwitter API returned ${res.status}`);
    }

    const data = await res.json();

    // Handle API-level errors
    if (data.error) {
      return {
        content: [{ type: "text", text: `Tweet not found or unavailable: ${data.error}` }],
      };
    }

    const media =
      data.media_extended?.map((m) => `[${m.type}] ${m.url}`).join("\n") || null;

    const lines = [
      `Author: ${data.user_name} (@${data.user_screen_name})`,
      `Date:   ${data.date}`,
      ``,
      data.text,
    ];

    // Surface X article content when the tweet links to one
    if (data.article) {
      lines.push(``, `Article: ${data.article.title}`);
      if (data.article.preview_text) {
        lines.push(`Preview: ${data.article.preview_text}`);
      }
    }

    lines.push(
      ``,
      `Likes: ${data.likes}  |  Retweets: ${data.retweets}  |  Replies: ${data.replies}`,
      `URL: ${data.tweetURL}`
    );

    if (media) lines.push(`Media:\n${media}`);

    const output = lines.join("\n");

    return { content: [{ type: "text", text: output }] };
  } catch (err) {
    return {
      content: [{ type: "text", text: `Error fetching tweet: ${err.message}` }],
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
