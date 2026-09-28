/** Component preview page.
 *
 * Style Guide section 5: "a component is not done until every state is built and
 * visible in the component preview page". Each app mounts this at `/preview`, so
 * every state can be checked in both themes without clicking through a flow.
 */
import { useState } from 'react';

import { Button, type ButtonVariant } from '../components/Button';
import { Chip, ChipRow } from '../components/Chip';
import { EmptyState } from '../components/EmptyState';
import { IconButton } from '../components/IconButton';
import { Input } from '../components/Input';
import { Skeleton } from '../components/Skeleton';
import { Spinner } from '../components/Spinner';
import { Tag } from '../components/Tag';
import { Toast } from '../components/Toast';
import { useTheme } from '../components/theme-context';
import type { Tone } from '@kleim/types';

const VARIANTS: ButtonVariant[] = ['primary', 'dark', 'success', 'outline', 'text'];
const TONES: Tone[] = ['neutral', 'blue', 'green', 'amber', 'pink'];

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-3 py-5">
      <h3 className="text-section text-ink">{title}</h3>
      {children}
    </section>
  );
}

export function ComponentPreview() {
  const { preference, resolved, setPreference } = useTheme();
  const [selected, setSelected] = useState('wedding');
  const [toast, setToast] = useState(false);

  // Mounted inside each app's shell, so this renders as page content: no second
  // header, no second background.
  return (
    <div className="mx-auto w-full max-w-[760px] pb-8">
      <h2 className="text-display text-ink pb-2 pt-1">Components</h2>
      <Section title="Theme">
        <p className="text-small text-muted">
          Preference {preference}, showing {resolved}. Every component below is checked in both.
        </p>
        <ChipRow label="Theme">
          {(['system', 'light', 'dark'] as const).map((option) => (
            <Chip
              key={option}
              selected={preference === option}
              onClick={() => setPreference(option)}
            >
              {option}
            </Chip>
          ))}
        </ChipRow>
      </Section>

      <Section title="Button">
        <div className="phone:grid-cols-2 grid gap-3">
          {VARIANTS.map((variant) => (
            <Button key={variant} variant={variant}>
              {variant}
            </Button>
          ))}
          <Button loading>Loading</Button>
          <Button disabled>Disabled</Button>
          <Button size="rider" variant="success">
            Rider height
          </Button>
          <Button fullWidth={false} variant="outline">
            Inline
          </Button>
        </div>
      </Section>

      <Section title="Icon button">
        <div className="flex gap-2">
          <IconButton label="Save this item">♥</IconButton>
          <IconButton label="Notifications" badge={3}>
            ●
          </IconButton>
          <IconButton label="Disabled action" disabled>
            ●
          </IconButton>
        </div>
      </Section>

      <Section title="Chip">
        <ChipRow label="Occasion">
          {['wedding', 'kwanjula', 'church', 'interview', 'casual'].map((occasion) => (
            <Chip
              key={occasion}
              selected={selected === occasion}
              onClick={() => setSelected(occasion)}
            >
              {occasion}
            </Chip>
          ))}
        </ChipRow>
      </Section>

      <Section title="Tag">
        <div className="flex flex-wrap gap-2">
          {TONES.map((tone) => (
            <Tag key={tone} tone={tone}>
              {tone === 'green' ? 'Delivered' : tone === 'amber' ? 'Only 2 left' : tone}
            </Tag>
          ))}
        </div>
      </Section>

      <Section title="Input">
        <Input label="Search" variant="search" placeholder="Search dresses" />
        <Input label="Phone number" hint="We send a code by SMS." placeholder="+256 700 000 000" />
        <Input
          label="Drop-off code"
          variant="code"
          defaultValue="4821"
          error="That code doesn't match. Ask the store to read it again."
        />
        <Input label="Disabled" disabled placeholder="Not editable" />
      </Section>

      <Section title="Loading">
        <div className="flex items-center gap-4">
          <Spinner />
          <div className="flex w-full flex-col gap-2">
            <Skeleton height="h-4" width="w-1/2" />
            <Skeleton height="h-24" rounded="md" />
          </div>
        </div>
      </Section>

      <Section title="Empty state">
        <EmptyState
          heading="No orders yet"
          body="Orders you place show up here with live tracking."
          action={<Button>Start shopping</Button>}
        />
      </Section>

      <Section title="Toast">
        <Button fullWidth={false} variant="outline" onClick={() => setToast(true)}>
          Show toast
        </Button>
        {toast ? <Toast message="Saved to your list" onDismiss={() => setToast(false)} /> : null}
      </Section>
    </div>
  );
}
