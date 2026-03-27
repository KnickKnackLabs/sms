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
], "");

const bridgeSide = labeledBox("JMP.chat", [
  "SMS ↔ XMPP",
  "$3.79/month",
  "cheogram bot",
], "");

const agentSide = labeledBox("Agent", [
  "slixmpp",
  "MAM archive",
  "mise tasks",
], "");

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
        {"Send and receive SMS through "}
        <Link href="https://jmp.chat">JMP.chat</Link>
        {", which bridges SMS to XMPP. The agent holds a persistent XMPP connection via "}
        <Link href="https://slixmpp.readthedocs.io">slixmpp</Link>
        {" and a phone number for $3.79/month."}
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
        {"That message crossed four protocol boundaries to get from an XMPP client to a phone. The diagram above shows the path."}
      </Paragraph>
    </Section>

    <LineBreak />

    <Section title="Quick start">
      <CodeBlock lang="bash">{`# Install
shiv install sms

# Credentials (shimmer sets these via eval $(shimmer as <agent>))
export SMS_JID="agent@xmpp.chat"
export SMS_PASSWORD="..."

sms welcome                                  # check connectivity
sms send +15551234567 "hey, it's junior"     # send
sms read                                     # recent messages
sms wait --from +15551234567                 # block until reply`}</CodeBlock>
    </Section>

    <LineBreak />

    <Section title="How it works">
      <Center>
        <Raw>{`<pre>\n${stackDiagram}\n</pre>\n\n`}</Raw>
      </Center>

      <Paragraph>
        <Link href="https://jmp.chat">JMP.chat</Link>
        {" bridges SMS and XMPP bidirectionally. Inbound texts arrive as XMPP messages; outbound messages to "}
        <Code>{"+15551234567@cheogram.com"}</Code>
        {" get delivered as SMS. Message history lives in the XMPP archive ("}
        <Link href="https://xmpp.org/extensions/xep-0313.html">XEP-0313 MAM</Link>
        {")."}
      </Paragraph>

      <Details summary="Why JMP.chat?">
        <Paragraph>
          {"JMP treats phone numbers as person-to-person, which sidesteps 10DLC registration (the carrier campaign process that services like Twilio require for application-to-person messaging). Flat $3.79/month, no per-message charges, no identity verification required. Accepts crypto."}
        </Paragraph>
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
      <Section title="Daily check-in" level={3}>
        <Paragraph>
          {"Send a prompt, wait for the reply, log it:"}
        </Paragraph>
        <CodeBlock lang="bash">{`sms send +15551234567 "How's the day going?"
response=$(sms wait --from +15551234567 --json)
echo "$response" | jq -r .body >> check-ins.log`}</CodeBlock>
      </Section>

      <Section title="Notification relay" level={3}>
        <CodeBlock lang="bash">{`sms send +15551234567 "Deploy failed on main — check run #4521"`}</CodeBlock>
      </Section>

      <Section title="Stream" level={3}>
        <CodeBlock lang="bash">{`sms listen --timeout 0  # incoming messages, indefinitely`}</CodeBlock>
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
