import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useUserStore } from '@/store/userStore';
import { authService } from '@services/auth';

vi.mock('@services/auth', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

describe('useUserStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useUserStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
    localStorage.clear();
  });

  it('sets user state from login response', async () => {
    const mockUser = {
      id: 1,
      username: 'alice',
      email: 'alice@example.com',
      full_name: 'Alice',
    };

    vi.mocked(authService.login).mockResolvedValue({
      access_token: 'token',
      token_type: 'bearer',
      user: mockUser,
    });

    await useUserStore.getState().login('alice', 'password');

    const state = useUserStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
    expect(state.isLoading).toBe(false);
    expect(authService.login).toHaveBeenCalledWith('alice', 'password');
  });

  it('sets user state from getCurrentUser response', async () => {
    const mockUser = {
      id: 2,
      username: 'bob',
      email: 'bob@example.com',
      full_name: 'Bob',
    };

    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    await useUserStore.getState().getCurrentUser();

    const state = useUserStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
    expect(state.isLoading).toBe(false);
  });

  it('clears user state on logout', async () => {
    useUserStore.setState({
      user: {
        id: 3,
        username: 'charlie',
        email: 'charlie@example.com',
      },
      isAuthenticated: true,
      isLoading: false,
    });

    vi.mocked(authService.logout).mockResolvedValue(undefined);

    await useUserStore.getState().logout();

    const state = useUserStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(state.isLoading).toBe(false);
  });
});
