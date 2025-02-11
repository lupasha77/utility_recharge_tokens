// frontend/src/App.tsx
import React from 'react'; 
import AppRoutes from './routes';
import { MantineProvider, ColorSchemeScript } from '@mantine/core';
import './utils/axiosConfig';
import '@mantine/core/styles.css'; 
import './styles/global.css';
import '@mantine/dates/styles.css';
import '@mantine/charts/styles.css';
// import '@mantine/notifications/styles.css';
// import { Notifications } from '@mantine/notifications';
  
  
  
  const App: React.FC = () => {
    // console.log('App loaded');
    return (
      <>
    <ColorSchemeScript defaultColorScheme="light" />
    <MantineProvider  >
      {/* <Notifications> */}
        <AppRoutes />
      {/* </Notifications> */}
    </MantineProvider>
    </>
  );
};

export default App;
