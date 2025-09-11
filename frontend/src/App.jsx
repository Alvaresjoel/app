import { RouterProvider, createBrowserRouter } from "react-router-dom";
import TasksPage from "./pages/Tasks.jsx";
import Login from "./pages/Login.jsx";
import { UserContextProvider } from "./store/user-context.jsx";
import RootPage from "./pages/Root.jsx";
import { action as loginAction } from "./pages/Login.jsx";
import { action as timesheetAction } from "./pages/Tasks.jsx"
import ChatPage from "./pages/Chat.jsx";
import { ToastContainer } from 'react-toastify';
import {chechAuth} from './services/auth.js'


const router = createBrowserRouter([
  {
    path: "/", element: <RootPage />, errorElement: <></>, children: [
      { index: true, element: <TasksPage />, action: timesheetAction, loader: chechAuth},
      { path: "dashboard" },
      { path: "chat", element: <ChatPage /> },

    ]
  },
  { path: "/login", element: <Login />, action: loginAction },
  { path: "/logout", element: <Login />, action: loginAction },
])

function App() {

  return (
    <UserContextProvider>

      <RouterProvider router={router} />
      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </UserContextProvider>
  );
}

export default App;
