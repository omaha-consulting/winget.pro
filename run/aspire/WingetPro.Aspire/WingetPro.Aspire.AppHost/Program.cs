using Aspire.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

var builder = DistributedApplication.CreateBuilder(args);

var django = builder.AddDockerfile("django", "../../../..", "run/aspire/Dockerfile")
    .WithVolume("static", "/srv/static")
    .WithVolume("winget.pro_uploaded_files", "/srv/media")
    .WithVolume("winget.pro_db_files", "/srv/db");

//Uncomment these lines the first time you run `dotnet run --project WingetPro.AppHost `:
//django
//    .WithEnvironment("DJANGO_SUPERUSER_USERNAME", "admin")
//    .WithEnvironment("DJANGO_SUPERUSER_EMAIL", "some@email.com")
//    .WithEnvironment("DJANGO_SUPERUSER_PASSWORD", "root");

var nginx = builder.AddDockerfile("nginx", "../../../..", "run/aspire/nginx.Dockerfile")
    .WithVolume("static", "/srv/static")
    .WithVolume("winget.pro_uploaded_files", "/srv/media")
    .WithVolume("nginx.conf", "/etc/nginx/nginx.conf:ro")
    .WithHttpEndpoint(targetPort: 80)
    .WithHttpsEndpoint(targetPort: 443, name:"secure")
    .WithBuildArg("CERTIFICATE_NAME", "localhost")
    .WithBuildArg("CERTIFICATE_PASSWORD", "test")
    .WithBuildArg("CERTIFICATE_SUBJECT", "localhost")
    .WithBuildArg("CERTIFICATE_DNS_NAME", "localhost")
    .WaitFor(django);

builder.Eventing.Subscribe<AfterEndpointsAllocatedEvent>((@event, cancellationToken) =>
    {
        nginx.WithBuildArg("SECURE_PORT", nginx.GetEndpoint("secure").Port);
        return Task.CompletedTask;
    }
);


builder.Build().Run();