import { Group, Button, useMantineColorScheme, useComputedColorScheme, Box, Flex, Menu, Avatar } from "@mantine/core";
import { IconSun, IconMoon, IconUser, IconLogout } from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuthHook";
import { useEffect, useCallback } from "react";

export function ThemeToggle() {
  const { setColorScheme } = useMantineColorScheme();
  const computedColorScheme = useComputedColorScheme("light", {
    getInitialValueInEffect: true,
  });

  return (
    <Button
      onClick={() =>
        setColorScheme(computedColorScheme === "light" ? "dark" : "light")
      }
      variant="default"
      leftSection={
        computedColorScheme === "light" ? (
          <IconMoon size={18} />
        ) : (
          <IconSun size={18} />
        )
      }
      px="sm"
    />
  );
}

export function HeaderMegaMenu() {
  const navigate = useNavigate();
  const { user, logout, isLoggedIn } = useAuth() as { user: { email: string; avatar?: string } | null; logout: () => Promise<void>; isLoggedIn: boolean };

  // Debugging Logs
  // console.log("Auth State - isLoggedIn:", isLoggedIn);
  // console.log("Auth State - User:", user);
  // console.log("Local Storage - accessToken:", sessionStorage.getItem("accessToken"));
  // console.log("Local Storage - user:", sessionStorage.getItem("user"));
  
  // Ensure the avatar URL is being correctly formed
  const avatarUrl = user?.avatar?.startsWith("data:image")
  ? user.avatar
  : user?.avatar
  ? `http://localhost:5000/api/files/uploads/${user.avatar}`
  : "/default-avatar.png";

  // console.log("Avatar URL:", avatarUrl);

  // Use useCallback to stabilize the function reference
  const handleLogout = useCallback(async () => {
    try {
      // console.log("Logging out...");
      await logout();
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
      sessionStorage.clear();
      navigate("/login");
    }
  }, [logout, navigate]);

  useEffect(() => {
    // Check if user is still authenticated
    const accessToken = sessionStorage.getItem("accessToken");

    if (!accessToken && isLoggedIn) {
      console.warn("User is logged in but no access token found. Logging out...");
      handleLogout();
    }
  }, [isLoggedIn, handleLogout]);

  return (
    <Box bg="cyan.6">
      <Flex h={60} px="md" justify="space-between" align="center" gap={5}>
        <Group>
          <Button variant="subtle" onClick={() => navigate("/")}>
            Home
          </Button>
          <Button variant="subtle">News</Button>
          <Button variant="subtle">Projects</Button>
        </Group>

        <Group>
          <ThemeToggle />
          {isLoggedIn && user ? (
            <Menu shadow="md" width={200} position="bottom-end">
              <Menu.Target>
                <Avatar
                  src={avatarUrl } // Fallback image if avatar URL is not valid
                  alt={user.email}
                  style={{ cursor: "pointer" }}
                  radius="xl"
                />
              </Menu.Target>
              <Menu.Dropdown>
                <Menu.Item
                  leftSection={<IconUser size={14} />}
                  onClick={() => navigate("/dashboard/profile")}
                >
                  Profile
                </Menu.Item>
                <Menu.Item
                  leftSection={<IconLogout size={14} />}
                  onClick={handleLogout}
                >
                  Logout
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          ) : (
            <>
              <Button variant="default" onClick={() => navigate("/login")}>
                Login
              </Button>
              <Button onClick={() => navigate("/register")}>Sign Up</Button>
            </>
          )}
        </Group>
      </Flex>
    </Box>
  );
}

export default HeaderMegaMenu;
