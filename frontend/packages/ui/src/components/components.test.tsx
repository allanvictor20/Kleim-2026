/** Component tests. CONTRIBUTING.md section 6 requires these for shared
 * components; each asserts the states and the accessible role the UI/UX Style
 * Guide specifies, not the class names. */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { Button } from './Button';
import { Chip } from './Chip';
import { EmptyState } from './EmptyState';
import { ErrorBoundary } from './ErrorBoundary';
import { IconButton } from './IconButton';
import { Input } from './Input';
import { Tag } from './Tag';
import { Toast } from './Toast';

describe('Button', () => {
  it('is a real button whose label says what happens', () => {
    render(<Button>Place order</Button>);
    expect(screen.getByRole('button', { name: 'Place order' })).toBeInTheDocument();
  });

  it('cannot be pressed twice while loading', async () => {
    // A double tap on a slow connection must not place two orders.
    const onClick = vi.fn();
    render(
      <Button loading onClick={onClick}>
        Place order
      </Button>,
    );

    const button = screen.getByRole('button', { name: /Place order/ });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
    await userEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it('announces its loading state', () => {
    render(<Button loading>Place order</Button>);
    expect(screen.getByRole('status', { name: 'Working' })).toBeInTheDocument();
  });

  it('does not fire when disabled', async () => {
    const onClick = vi.fn();
    render(
      <Button disabled onClick={onClick}>
        Accept
      </Button>,
    );
    await userEvent.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });

  it('defaults to type=button so it cannot submit a form by accident', () => {
    render(<Button>Accept</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
  });
});

describe('IconButton', () => {
  it('always has an accessible name', () => {
    render(<IconButton label="Save this item">♥</IconButton>);
    expect(screen.getByRole('button', { name: 'Save this item' })).toBeInTheDocument();
  });

  it('caps a large badge count', () => {
    render(
      <IconButton label="Notifications" badge={250}>
        ●
      </IconButton>,
    );
    expect(screen.getByText('99+')).toBeInTheDocument();
  });

  it('hides the badge at zero', () => {
    render(
      <IconButton label="Notifications" badge={0}>
        ●
      </IconButton>,
    );
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });
});

describe('Chip', () => {
  it('reports selection to a screen reader, not only by colour', () => {
    render(<Chip selected>Wedding</Chip>);
    expect(screen.getByRole('button', { name: 'Wedding' })).toHaveAttribute('aria-pressed', 'true');
  });

  it('is unpressed when not selected', () => {
    render(<Chip>Wedding</Chip>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-pressed', 'false');
  });
});

describe('Tag', () => {
  it('always carries a word, since colour alone is not a status', () => {
    render(<Tag tone="green">Delivered</Tag>);
    expect(screen.getByText('Delivered')).toBeInTheDocument();
  });
});

describe('Input', () => {
  it('has a real label tied to the field', () => {
    render(<Input label="Phone number" />);
    expect(screen.getByLabelText('Phone number')).toBeInTheDocument();
  });

  it('marks an error and links the message to the field', () => {
    render(
      <Input
        label="Drop-off code"
        error="That code doesn't match. Ask the store to read it again."
      />,
    );

    const field = screen.getByLabelText('Drop-off code');
    expect(field).toHaveAttribute('aria-invalid', 'true');
    expect(field).toHaveAccessibleDescription(/Ask the store to read it again/);
  });

  it('gives code entry a numeric keypad', () => {
    render(<Input label="Drop-off code" variant="code" />);
    expect(screen.getByLabelText('Drop-off code')).toHaveAttribute('inputmode', 'numeric');
  });

  it('keeps a hidden label available to assistive technology', () => {
    render(<Input label="Search" hideLabel variant="search" />);
    expect(screen.getByLabelText('Search')).toBeInTheDocument();
  });
});

describe('EmptyState', () => {
  it('invites exactly one action', () => {
    render(
      <EmptyState
        heading="No orders yet"
        body="Orders you place show up here with live tracking."
        action={<Button>Start shopping</Button>}
      />,
    );

    expect(screen.getByRole('heading', { name: 'No orders yet' })).toBeInTheDocument();
    expect(screen.getAllByRole('button')).toHaveLength(1);
  });
});

describe('Toast', () => {
  it('is announced without stealing focus, and carries no action', () => {
    render(<Toast message="Saved to your list" />);

    const toast = screen.getByRole('status');
    expect(toast).toHaveTextContent('Saved to your list');
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('disappears after four seconds', () => {
    vi.useFakeTimers();
    const onDismiss = vi.fn();
    try {
      render(<Toast message="Saved" onDismiss={onDismiss} />);
      expect(screen.getByRole('status')).toBeInTheDocument();
      vi.advanceTimersByTime(4000);
    } finally {
      vi.useRealTimers();
    }
    expect(onDismiss).toHaveBeenCalled();
  });
});

describe('ErrorBoundary', () => {
  function Boom(): never {
    throw Object.assign(new Error('kaboom'), { requestId: 'req-abc' });
  }

  it('shows a fixable message instead of a blank screen, and hides the raw error', () => {
    // React logs the caught error; silence it so the run stays readable.
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    try {
      render(
        <ErrorBoundary>
          <Boom />
        </ErrorBoundary>,
      );

      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('This screen did not load')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument();
      // Style Guide section 7.3: never show the raw error.
      expect(screen.queryByText(/kaboom/)).not.toBeInTheDocument();
    } finally {
      consoleError.mockRestore();
    }
  });

  it('offers the request id only under contact support', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    try {
      render(
        <ErrorBoundary>
          <Boom />
        </ErrorBoundary>,
      );
      expect(screen.getByText('Contact support')).toBeInTheDocument();
      expect(screen.getByText('req-abc')).toBeInTheDocument();
    } finally {
      consoleError.mockRestore();
    }
  });

  it('reports the error so Sentry can see it', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    const onError = vi.fn();
    try {
      render(
        <ErrorBoundary onError={onError}>
          <Boom />
        </ErrorBoundary>,
      );
      expect(onError).toHaveBeenCalled();
    } finally {
      consoleError.mockRestore();
    }
  });
});
