/** @jsxImportSource jsx-md */

import { readdirSync, readFileSync } from "fs";
import { join } from "path";

import {
  Badge,
  Badges,
  Bold,
  Center,
  Code,
  CodeBlock,
  Details,
  Heading,
  Item,
  Link,
  List,
  Paragraph,
  Section,
} from "readme";

const testDir = join(import.meta.dirname, "tests");
const testSource = readdirSync(testDir)
  .filter((name) => name.endsWith(".bats"))
  .map((name) => readFileSync(join(testDir, name), "utf-8"))
  .join("\n");
const testCount = (testSource.match(/@test /g) || []).length;

const readme = (
  <>
    <Center>
      <Heading level={1}>sms</Heading>

      <Paragraph>
        <Bold>SMS tools</Bold>
      </Paragraph>

      <Paragraph>
        {"Send and receive SMS through "}
        <Link href="https://jmp.chat">JMP.chat</Link>
        {" using an XMPP account."}
      </Paragraph>

      <Badges>
        <Badge label="tests" value={`${testCount}`} color="blue" />
        <Badge label="License" value="MIT" color="blue" href="LICENSE" />
      </Badges>
    </Center>

    <Section title="Install">
      <Paragraph>
        {"Start with an XMPP account linked to a JMP.chat number. Follow "}
        <Link href="https://jmp.chat">JMP.chat's setup instructions</Link>
        {" to activate the account, then provide its XMPP credentials:"}
      </Paragraph>

      <CodeBlock lang="bash">{`shiv install sms

export SMS_JID="agent@xmpp.chat"
export SMS_PASSWORD="..."

sms status  # Check connection and authentication`}</CodeBlock>

      <Paragraph>
        {
          "Keep credentials outside the repository. For message history, enable archiving:"
        }
      </Paragraph>

      <CodeBlock lang="bash">{`sms archive enable
sms archive status`}</CodeBlock>
    </Section>

    <Section title="Run">
      <CodeBlock lang="bash">{`# Send through the gateway using the recipient's full XMPP JID
sms message send +15551234567@cheogram.com "Hello from the terminal"

# Read the ten most recent archived messages
sms message read --limit 10

# Wait up to five minutes for one incoming message, then return JSON
sms message listen --once --timeout 300 --json

# Or stream incoming messages as JSON Lines until interrupted
sms message listen --json`}</CodeBlock>
    </Section>

    <Details summary="Notes">
      <List>
        <Item>
          <Bold>Addressing.</Bold>
          {" Sending takes a full XMPP JID, such as "}
          <Code>+15551234567@cheogram.com</Code>
        </Item>
        <Item>
          <Bold>Contacts.</Bold>
          {
            " Some servers filter messages from unlisted senders. Add a phone JID to the roster with "
          }
          <Code>sms contact add +15551234567@cheogram.com</Code>
        </Item>
        <Item>
          <Bold>History.</Bold>
          {" Archive reading uses the server's "}
          <Link href="https://xmpp.org/extensions/xep-0313.html">
            MAM archive
          </Link>
          {". Don't forget to enable archiving, if you need it."}
        </Item>
        <Item>
          <Bold>Delivery.</Bold>
          {" The send command confirms queuing, rather than carrier delivery."}
        </Item>
      </List>
    </Details>
  </>
);

console.log(readme);
