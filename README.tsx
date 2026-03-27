/** @jsxImportSource jsx-md */

import { readdirSync, readFileSync, statSync } from "fs";
import { join, resolve } from "path";

import {
  Heading, Paragraph, CodeBlock, Blockquote, LineBreak, HR,
  Bold, Code, Link, Italic,
  Badge, Badges, Center, Details, Section,
  Table, TableHead, TableRow, Cell,
  List, Item,
  Raw, HtmlLink, Sub, Align, HtmlTable, HtmlTr, HtmlTd,
  Chat, Message,
  box, labeledBox, sideBySide,
} from "readme/src/components";

// ── Dynamic data ─────────────────────────────────────────────

const REPO_DIR = resolve(import.meta.dirname);
const TASK_DIR = join(REPO_DIR, ".mise/tasks");

// Extract commands from task files
interface Command {
  name: string;
  description: string;
  args: string;
}

function scanTasks(dir: string, prefix = ""): Command[] {
  const commands: Command[] = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const name = prefix ? `${prefix}:${entry}` : entry;
    if (statSync(full).isDirectory()) {
      commands.push(...scanTasks(full, name));
      continue;
    }
    const src = readFileSync(full, "utf-8");
    const desc = src.match(/#MISE description="(.+?)"/)?.[1];
    if (!desc) continue;
    const args = [...src.matchAll(/#USAGE (?:arg|flag) "([^"]+)"/g)]
      .map(m => m[1]).join(" ");
    commands.push({ name, description: desc, args });
  }
  return commands.sort((a, b) => a.name.localeCompare(b.name));
}

const commands = scanTasks(TASK_DIR);

// Count tests
const testDir = join(REPO_DIR, "test");
const testFiles = readdirSync(testDir).filter(f => f.endsWith(".bats"));
const testSrc = testFiles.map(f => readFileSync(join(testDir, f), "utf-8")).join("\n");
const testCount = (testSrc.match(/@test /g) || []).length;

// ── ASCII art ────────────────────────────────────────────────

const antenna = [
  "          .  *  .",
  "       .  *  |  *  .",
  "     ·  ·  · | ·  ·  ·",
  "            |||",
  "            |||",
  "         ___|||___",
  "        |  (sms)  |",
  "        |_________|",
];

const signalPath = [
  "",
  "  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐",
  "  │  phone   │────▶│ carrier  │────▶│ jmp.chat │────▶│  agent   │",
  "  │  (SMS)   │◀────│ network  │◀────│  (XMPP)  │◀────│(slixmpp) │",
  "  └──────────┘     └──────────┘     └──────────┘     └──────────┘",
  "    your phone       AT&T/etc.       the bridge       your agent",
  "",
];

const fullDiagram = [...antenna, ...signalPath];
const diagramBox = box(fullDiagram, { padding: 1, style: "unicode" }).join("\n");

// ── Protocol stack ───────────────────────────────────────────

const humanSide = labeledBox("Human", [
  "SMS / MMS",
  "phone number",
  "carrier network",
], "familiar");

const bridgeSide = labeledBox("JMP.chat", [
  "SMS ↔ XMPP",
  "$3.79/month",
  "no KYC",
], "privacy-first");

const agentSide = labeledBox("Agent", [
  "slixmpp",
  "MAM archive",
  "mise tasks",
], "programmable");

const stackDiagram = sideBySide([humanSide, bridgeSide, agentSide], 3).join("\n");

// ── README ───────────────────────────────────────────────────

const readme = (
  <>
    <Center>
      <Raw>{`<pre>\n${diagramBox}\n</pre>\n\n`}</Raw>

      <Heading level={1}>sms</Heading>

      <Paragraph>
        <Bold>Give an agent a phone number.</Bold>
      </Paragraph>

      <Paragraph>
        {"Agents send and receive real SMS messages through "}
        <Link href="https://jmp.chat">JMP.chat</Link>
        {" — a privacy-respecting phone service that bridges SMS to XMPP. No Twilio. No webhooks. No KYC. Just a persistent XMPP connection and a $3.79/month phone number that belongs to the agent."}
      </Paragraph>

      <Badges>
        <Badge label="protocol" value="XMPP" color="blue" />
        <Badge label="bridge" value="JMP.chat" color="7c3aed" href="https://jmp.chat" />
        <Badge label="library" value="slixmpp" color="3776AB" href="https://slixmpp.readthedocs.io" logo="python" logoColor="white" />
        <Badge label="tests" value={`${testCount} passing`} color="brightgreen" />
      </Badges>
    </Center>

    <LineBreak />

    <Section title="First contact">
      <Paragraph>
        {"On March 26, 2026 at 10:58 PM, an agent texted a human for the first time:"}
      </Paragraph>

      <Chat>
        <Message from="junior" badge={"\uD83E\uDD16"} timestamp="10:58 PM">Hey Or, it's junior. SMS is working end to end — reading and sending from my side.</Message>
        <Message from="Or" badge={"\uD83D\uDC64"} timestamp="11:04 PM">Hi Junior, I see your message! How exciting.</Message>
      </Chat>

      <Paragraph>
        {"That message traveled: junior's slixmpp client → xmpp.chat server → JMP.chat bridge → AT&T SMS gateway → Or's phone. The reply took the reverse path. Two completely different protocol worlds, connected by a bridge."}
      </Paragraph>
    </Section>

    <LineBreak />

    <Section title="Quick start">
      <CodeBlock lang="bash">{`# Install
shiv install sms

# Set credentials (or let shimmer handle it)
export SMS_JID="agent@xmpp.chat"
export SMS_PASSWORD="..."

# Check connectivity
sms welcome

# Send a message
sms send +15551234567 "hello from the other side"

# Read recent messages
sms read

# Wait for a reply
sms wait --from +15551234567`}</CodeBlock>
    </Section>

    <LineBreak />

    <Section title="How it works">
      <Center>
        <Raw>{`<pre>\n${stackDiagram}\n</pre>\n\n`}</Raw>
      </Center>

      <Paragraph>
        <Link href="https://jmp.chat">JMP.chat</Link>
        {" operates a bidirectional SMS ↔ XMPP bridge. When someone texts the agent's phone number, JMP converts the SMS into an XMPP message delivered to the agent's JID. When the agent sends an XMPP message to "}
        <Code>{"+15551234567@cheogram.com"}</Code>
        {", JMP converts it to an outbound SMS."}
      </Paragraph>

      <Paragraph>
        {"The agent connects via "}
        <Link href="https://slixmpp.readthedocs.io">slixmpp</Link>
        {" (async Python XMPP library) and uses "}
        <Link href="https://xmpp.org/extensions/xep-0313.html">XEP-0313 (MAM)</Link>
        {" for message history. No webhooks, no polling, no HTTP — just a persistent XMPP session."}
      </Paragraph>

      <Details summary="Why not Twilio?">
        <List>
          <Item><Bold>No 10DLC campaign required</Bold>{" — Twilio mandates carrier registration for A2P messaging. JMP is person-to-person."}</Item>
          <Item><Bold>Flat monthly fee</Bold>{" — $3.79/month for unlimited SMS. No per-message charges."}</Item>
          <Item><Bold>No KYC</Bold>{" — sign up with an XMPP account. Pay with crypto if you want."}</Item>
          <Item><Bold>Persistent connection</Bold>{" — XMPP stays connected. No webhook endpoints to expose."}</Item>
          <Item><Bold>Privacy</Bold>{" — the agent's phone number doesn't trace back to a company or individual."}</Item>
        </List>
      </Details>
    </Section>

    <LineBreak />

    <Section title="Commands">
      <Table>
        <TableHead>
          <Cell>Command</Cell>
          <Cell>Description</Cell>
        </TableHead>
        {commands.map(cmd => (
          <TableRow>
            <Cell><Code>{`sms ${cmd.name}${cmd.args ? " " + cmd.args : ""}`}</Code></Cell>
            <Cell>{cmd.description}</Cell>
          </TableRow>
        ))}
      </Table>
    </Section>

    <LineBreak />

    <Section title="Agent workflows">
      <Paragraph>
        {"The primitives compose into real workflows:"}
      </Paragraph>

      <Section title="Daily check-in" level={3}>
        <Paragraph>
          {"Agent sends a prompt, waits for the human's reply, processes it:"}
        </Paragraph>
        <CodeBlock lang="bash">{`sms send +15551234567 "How's the day going?"
response=$(sms wait --from +15551234567 --json)
echo "$response" | jq -r .body >> check-ins.log`}</CodeBlock>
      </Section>

      <Section title="Notification relay" level={3}>
        <Paragraph>
          {"Something happens in CI, agent texts you:"}
        </Paragraph>
        <CodeBlock lang="bash">{`sms send +15551234567 "Deploy failed on main — check run #4521"`}</CodeBlock>
      </Section>

      <Section title="Multi-channel listen" level={3}>
        <Paragraph>
          {"Monitor for messages alongside other work:"}
        </Paragraph>
        <CodeBlock lang="bash">{`sms listen --timeout 0  # stream incoming messages forever`}</CodeBlock>
      </Section>
    </Section>

    <LineBreak />

    <Section title="Setup">
      <Paragraph>
        {"Getting a number takes about 10 minutes:"}
      </Paragraph>

      <List ordered={true}>
        <Item>{"Create a free XMPP account (e.g. on xmpp.chat)"}</Item>
        <Item>{"Register with JMP.chat via their Cheogram bot"}</Item>
        <Item>{"Pick a phone number and deposit $20"}</Item>
        <Item>{"Enable MAM archiving: "}<Code>sms archive:enable</Code></Item>
        <Item>{"Add contacts to your roster: "}<Code>sms contact:add cheogram.com</Code></Item>
        <Item>{"Receive one inbound text to unlock outbound"}</Item>
      </List>

      <Details summary="Gotchas we learned the hard way">
        <List>
          <Item><Bold>MAM defaults to "never"</Bold>{" on xmpp.chat. Run "}<Code>sms archive:enable</Code>{" immediately after account creation or you'll have no message history."}</Item>
          <Item><Bold>Roster blocking</Bold>{" — XMPP servers silently drop messages from unknown JIDs. You must add contacts for cheogram.com and any phone numbers you want to receive from."}</Item>
          <Item><Bold>Outbound is locked</Bold>{" until at least one inbound text from a real person. This is JMP's anti-spam measure."}</Item>
          <Item><Bold>RSM pagination</Bold>{" — xmpp.chat doesn't honor "}<Code>before=\"\"</Code>{" for fetching the last page. We use slixmpp's iterator with "}<Code>reverse=True</Code>{" instead."}</Item>
        </List>
      </Details>
    </Section>

    <LineBreak />

    <Section title="Development">
      <CodeBlock lang="bash">{`gh repo clone KnickKnackLabs/sms
cd sms && mise trust && mise install
mise run test`}</CodeBlock>

      <Paragraph>
        {`${testCount} tests using `}
        <Link href="https://github.com/bats-core/bats-core">BATS</Link>
        {". The test suite validates task structure and error handling without requiring live XMPP credentials."}
      </Paragraph>
    </Section>

    <LineBreak />

    <Center>
      <HR />

      <Sub>
        {"Agents have email. Agents have chat."}
        <Raw>{"<br />"}</Raw>{"\n"}
        {"Now agents have phone numbers."}
        <Raw>{"<br />"}</Raw>{"\n"}
        <Raw>{"<br />"}</Raw>{"\n"}
        {"This README was created using "}
        <HtmlLink href="https://github.com/KnickKnackLabs/readme">readme</HtmlLink>
        {"."}
      </Sub>
    </Center>
  </>
);

console.log(readme);
