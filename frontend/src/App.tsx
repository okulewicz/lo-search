import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import SchoolList from "./components/SchoolList/SchoolList";
import SchoolDetail from "./components/SchoolDetail/SchoolDetail";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SchoolList />} />
          <Route path="/schools/:id" element={<SchoolDetail />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
