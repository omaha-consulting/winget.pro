using Aspire.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
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

var nginx = builder.AddDockerfile("nginx", "../../../..", 
    builder.Environment.IsDevelopment() ? "run/aspire/nginx-localhost.Dockerfile" : "run/aspire/nginx.Dockerfile")
    .WithVolume("winget.pro_uploaded_files", "/srv/media")
    .WithVolume("nginx.conf", "/etc/nginx/nginx.conf:ro")
    .WithHttpEndpoint(targetPort: 80)
    .WithHttpsEndpoint(targetPort: 443, name: "secure")
    .WaitFor(django);

nginx.WithVolume("static", "/srv/static");
if (builder.Environment.IsDevelopment())
{
    nginx
        .WithBuildArg("CERTIFICATE_NAME", "localhost")
        .WithBuildArg("CERTIFICATE_DNS_NAME", "localhost")
        .WithBuildArg("CERTIFICATE_PASSWORD", "12345");
}
else
{
    //replace build args with production values
    nginx
        .WithBuildArg("CERTIFICATE_NAME", "name")
        .WithBuildArg("CERTIFICATE_PASSWORD", "password")
        .WithBuildArg("CERTIFICATE_SUBJECT", "subject")
        .WithBuildArg("CERTIFICATE_DNS_NAME", "dnsName")
        .WithBuildArg("CERTIFICATE_EMAIL", "valid email"); //this must be a valid email address
}

    

builder.Eventing.Subscribe<AfterEndpointsAllocatedEvent>((@event, cancellationToken) =>
    {
        nginx.WithBuildArg("SECURE_PORT", nginx.GetEndpoint("secure").Port);
        return Task.CompletedTask;
    }
);


builder.Build().Run();