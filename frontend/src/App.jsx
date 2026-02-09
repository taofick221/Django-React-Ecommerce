import { useEffect, useState } from "react";

function Products() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/products/")
      .then(res => res.json())
      .then(data => setProducts(data));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-800">
      <h1 className="text-3xl font-bold text-center py-6">
        Product List
      </h1>

      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map(product => (
            <div
              key={product.id}
              className="bg-white p-4 rounded-lg shadow hover:shadow-md transition"
            >
              <h2 className="text-lg font-semibold">
                {product.name}
              </h2>

              <p className="text-gray-600 text-sm mt-1">
                {product.description || "No description"}
              </p>

              <p className="text-gray-800 font-bold mt-2">
                ৳{product.price}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Products;
