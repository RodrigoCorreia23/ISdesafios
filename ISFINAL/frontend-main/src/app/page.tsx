
import LeafleatMap from "./components/MainMap";
import Sidebar from "./components/MainSideBar";
import { GraphQlWarehouses } from "./interface";

const getMapaData = async (search: string = "") => {
  "use server";

  const headers = {
    "content-type": "application/json",
  };

  const options = {
    method: "POST",
    headers,
    body: JSON.stringify({ search }),
  };

  const response = await fetch(`${process.env.REST_API_BASE_URL}/api/get-warehouses/`, options);

  if (!response.ok) {
    throw new Error(`Failed to fetch warehouses data: ${response.statusText}`);
  }

  const { data } = await response.json();

  // Transformar os dados brutos retornados pelo backend
  const transformedData = {
    data: {
      warehouses: data.map((warehouse: any) => ({
        id: warehouse.id,
        region: warehouse.warehouse,
        product_line: warehouse.product_line,
        latitude: warehouse.latitude,
        longitude: warehouse.longitude,
      })),
    },
  };

  return transformedData;
};

const updatePoint = async(id: number, latitude: number, longitude: number) => {
  "use server"

  const headers = {
    'content-type': 'application/json',
  }

  const options = {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      latitude: latitude,
      longitude: longitude
    })
  }

  const response = await fetch(`${process.env.REST_API_BASE_URL}/api/warehouses/${id}/`, options);

  return await response.json()
}

export default async function Home({ searchParams }: {searchParams : any}) {
  const params: any = await searchParams

  const search: string = params?.search ?? ''

  const mapa_data: GraphQlWarehouses = await getMapaData(search)

  return (
    <div className="h-[100vh] w-full">
      <nav className="w-[250px] h-full absolute left-0">
        <Sidebar searchValue={search} />
      </nav>
      <main className="h-full" style={{ marginLeft: 250}}>
        <LeafleatMap warehouses={mapa_data.data.warehouses} updatePoint={updatePoint} />
      </main>
    </div>
  );
}
