// NavbarLinksGroup.tsx
import React from 'react';
import { Group, Anchor } from '@mantine/core';

interface NavbarLinksGroupProps {
  links: { label: string; link: string }[];
}

const NavbarLinksGroup: React.FC<NavbarLinksGroupProps> = ({ links }) => {
  return (
    <Group>
      {links.map((link, index) => (
        <Anchor key={index} href={link.link}>
          {link.label}
        </Anchor>
      ))}
    </Group>
  );
};

export { NavbarLinksGroup };