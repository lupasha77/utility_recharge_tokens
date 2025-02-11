
import { useState } from "react";
import { Modal,Drawer, Button, Text,Popover } from "@mantine/core";
 

export const SimpleModalTest = () => {
  const [opened, setOpened] = useState(false);

  return (
    <>
      <Button onClick={() => setOpened(true)}>Open Modal</Button>
      <Modal opened={opened} onClose={() => setOpened(false)} title="Test Modal">
        <Button onClick={() => setOpened(false)}>Close Modal</Button>
      </Modal>
    </>
  );
};



export const PopoverTest = () => {
  const [opened, setOpened] = useState(false);

  return (
    <Popover
      opened={opened}
      onClose={() => setOpened(false)}
    >
      <Popover.Target>
        <Button onClick={() => setOpened(true)}>Open Popover</Button>
      </Popover.Target>
      <Popover.Dropdown>
        <Text>Popover Content Here</Text>
        <Button onClick={() => setOpened(false)}>Close Popover</Button>
      </Popover.Dropdown>
    </Popover>
  );
};

 


export const DrawerTest = () => {
  const [opened, setOpened] = useState(false);

  return (
    <>
      <Button onClick={() => setOpened(true)}>Open Drawer</Button>
      <Drawer opened={opened} onClose={() => setOpened(false)} title="Test Drawer">
        <Text>Drawer Content</Text>
        <Button onClick={() => setOpened(false)}>Close Drawer</Button>
      </Drawer>
    </>
  );
};


